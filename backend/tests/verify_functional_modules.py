
import sys
import os
import uuid
from datetime import datetime, date
from decimal import Decimal

# Add backend directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.database import SessionLocal
from app.models.company import Company
from app.models.policy import Policy
from app.models.payment import Payment
from app.models.claim import Claim
from app.models.co_insurance import CoInsuranceShare
from app.models.inter_company_share import InterCompanyShare
from app.services.payment_service import PaymentService
from app.services.claim_service import ClaimService
from app.repositories.payment_repository import PaymentRepository

def verify_flows():
    db = SessionLocal()
    try:
        # 1. Setup - Get or Create Companies
        lead_company = db.query(Company).filter(Company.name == "Lead Insurer").first()
        if not lead_company:
            lead_company = Company(id=uuid.uuid4(), name="Lead Insurer", subdomain=f"lead-{uuid.uuid4().hex[:4]}", email="lead@example.com")
            db.add(lead_company)
        
        partner_company = db.query(Company).filter(Company.name == "Partner Insurer").first()
        if not partner_company:
            partner_company = Company(id=uuid.uuid4(), name="Partner Insurer", subdomain=f"partner-{uuid.uuid4().hex[:4]}", email="partner@example.com")
            db.add(partner_company)
        
        db.commit()
        
        from app.models.client import Client
        client_id = uuid.uuid4()
        new_client = Client(
            id=client_id,
            company_id=lead_company.id,
            client_type="individual",
            first_name="Test",
            last_name="User",
            email=f"test-{uuid.uuid4().hex[:4]}@example.com",
            phone="+123456789",
            status="active"
        )
        db.add(new_client)
        db.commit()
        
        # 2. Create a Policy with Co-insurance
        policy_id = uuid.uuid4()
        new_policy = Policy(
            id=policy_id,
            company_id=lead_company.id,
            client_id=client_id, 
            policy_number=f"POL-TEST-{uuid.uuid4().hex[:4]}",
            premium_amount=Decimal("100000.00"),
            start_date=date(2025, 1, 1),
            end_date=date(2025, 12, 31),
            status='active'
        )
        db.add(new_policy)
        
        # 30% share for Partner
        share = CoInsuranceShare(
            policy_id=policy_id,
            company_id=partner_company.id,
            share_percentage=Decimal("30.00"),
            fee_percentage=Decimal("5.00") # 5% management fee
        )
        db.add(share)
        db.commit()
        print(f"Policy {new_policy.policy_number} created with 30% co-insurance.")

        # 3. Test Payment & Premium Distribution
        print("\nTesting Premium Distribution...")
        payment_repo = PaymentRepository(db)
        payment_service = PaymentService(payment_repo)
        
        payment = payment_service.create_payment(
            company_id=lead_company.id,
            policy_id=policy_id,
            client_id=new_policy.client_id,
            amount=Decimal("100000.00"),
            payment_method="cash"
        )
        
        # Process payment (this should trigger distribution)
        payment_service.process_payment(payment.id, {"status": "success"})
        
        # Verify InterCompanyShare for premium
        premium_share = db.query(InterCompanyShare).filter(
            InterCompanyShare.from_company_id == lead_company.id,
            InterCompanyShare.to_company_id == partner_company.id,
            InterCompanyShare.resource_type == "premium_distribution",
            InterCompanyShare.resource_id == payment.id
        ).first()
        
        if premium_share:
            # Expected: (100000 * 30%) = 30000. Less 5% fee = 30000 - 1500 = 28500.
            print(f"SUCCESS: Premium share created for {premium_share.amount} {premium_share.currency}")
            if premium_share.amount == Decimal("28500.00"):
                print("Calculation is CORRECT (28500 after 5% fee).")
            else:
                print(f"Calculation is INCORRECT: Expected 28500, got {premium_share.amount}")
        else:
            print("FAILURE: Premium share record not found.")

        # 4. Test Claim & Settlement Distribution
        print("\nTesting Claim Settlement...")
        claim_service = ClaimService(db)
        from app.schemas.claim import ClaimCreate
        claim_data = ClaimCreate(
            policy_id=policy_id,
            company_id=lead_company.id,
            incident_date=date(2025, 6, 1),
            incident_description="Test incident",
            claim_amount=Decimal("50000.00")
        )
        
        claim = claim_service.create_claim(claim_data)
        print(f"Claim {claim.claim_number} created.")
        
        # Approve claim (this should trigger settlement)
        from app.schemas.claim import ClaimUpdate
        claim_service.update_claim(claim.id, ClaimUpdate(status="approved", approved_amount=Decimal("40000.00")))
        
        # Verify InterCompanyShare for claim
        claim_share = db.query(InterCompanyShare).filter(
            InterCompanyShare.from_company_id == lead_company.id,
            InterCompanyShare.to_company_id == partner_company.id,
            InterCompanyShare.resource_type == "claim_settlement",
            InterCompanyShare.resource_id == claim.id
        ).first()
        
        if claim_share:
            # Expected: 40000 * 30% = 12000.
            print(f"SUCCESS: Claim settlement shared for {claim_share.amount} {claim_share.currency}")
            if claim_share.amount == Decimal("12000.00"):
                print("Calculation is CORRECT (12000).")
            else:
                print(f"Calculation is INCORRECT: Expected 12000, got {claim_share.amount}")
        else:
            print("FAILURE: Claim settlement record not found.")

    finally:
        db.close()

if __name__ == "__main__":
    verify_flows()
