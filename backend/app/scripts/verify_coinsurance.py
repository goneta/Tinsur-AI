
import sys
import os
from decimal import Decimal
import uuid

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.core.database import SessionLocal
from app.models.policy import Policy
from app.models.claim import Claim
from app.models.co_insurance import CoInsuranceShare
from app.models.inter_company_share import InterCompanyShare
from app.services.claim_service import ClaimService
from app.schemas.claim import ClaimUpdate

def test_coinsurance_distribution():
    print("Testing Co-insurance Distribution Logic...")
    db = SessionLocal()
    try:
        # 1. Get a policy and a company to share with
        policy = db.query(Policy).first()
        if not policy:
            print("No policies found.")
            return

        # Use another company for sharing (arbitrary)
        from app.models.company import Company
        other_company = db.query(Company).filter(Company.id != policy.company_id).first()
        if not other_company:
            print("No other company found to share with.")
            # Create a mock one if needed, but usually there's one in seed
            other_company = Company(name="Test Partner", email="partner@test.com")
            db.add(other_company)
            db.commit()

        print(f"Policy: {policy.policy_number}")
        print(f"Sharing with: {other_company.name}")

        # 2. Add co-insurance share (30%)
        db.query(CoInsuranceShare).filter(CoInsuranceShare.policy_id == policy.id).delete()
        share = CoInsuranceShare(
            policy_id=policy.id,
            company_id=other_company.id,
            share_percentage=Decimal("30.00"),
            fee_percentage=Decimal("5.00")
        )
        db.add(share)
        db.commit()
        print("Share added: 30%")

        # 3. Create a claim
        service = ClaimService(db)
        from app.schemas.claim import ClaimCreate
        from datetime import date
        claim_data = ClaimCreate(
            policy_id=policy.id,
            incident_date=date.today(),
            incident_description="Test co-insurance claim",
            claim_amount=10000.0,
            company_id=policy.company_id
        )
        claim = service.create_claim(claim_data)
        print(f"Claim created: {claim.claim_number}, Amount: {claim.claim_amount}")

        # 4. Approve the claim
        print("Approving claim...")
        update = ClaimUpdate(status="approved", approved_amount=10000.0)
        service.update_claim(claim.id, update)

        # 5. Verify settlement generation
        settlement = db.query(InterCompanyShare).filter(
            InterCompanyShare.resource_id == claim.id,
            InterCompanyShare.resource_type == "claim_settlement"
        ).first()

        if settlement:
            print("SUCCESS: Inter-company settlement generated.")
            print(f"Settlement Details: {settlement.notes}")
            if "3000.0" in settlement.notes or "3000" in settlement.notes:
                print("SUCCESS: Settlement amount calculated correctly (30% of 10000).")
            else:
                print(f"WARNING: Check settlement amount calculation in notes: {settlement.notes}")
        else:
            print("FAILURE: No settlement generated.")

    finally:
        db.close()

if __name__ == "__main__":
    test_coinsurance_distribution()
