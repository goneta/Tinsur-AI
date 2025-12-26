
import sys
import os
from decimal import Decimal
from datetime import date
import asyncio
import uuid

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.core.database import SessionLocal, engine, Base
from app.models.claim import Claim
from app.models.recovery import ClaimRecovery
from app.services.recovery_service import RecoveryService
from app.models.company import Company

async def verify_claim_recovery_flow():
    print("Ensuring Recovery tables exist...")
    Base.metadata.create_all(bind=engine)
    
    print("Verifying Subrogation & Salvage Flow...")
    db = SessionLocal()
    try:
        company = db.query(Company).first()
        if not company:
            print("No company found for testing.")
            return
            
        # 1. Setup a dummy claim
        claim = db.query(Claim).filter(Claim.company_id == company.id).first()
        if not claim:
            print("Creating dummy claim for test...")
            from app.models.client import Client
            from app.models.policy import Policy
            from app.models.policy_type import PolicyType
            
            client = db.query(Client).filter(Client.company_id == company.id).first()
            if not client:
                client = Client(company_id=company.id, first_name="Test", last_name="User", email=f"test_{uuid.uuid4().hex[:4]}@example.com")
                db.add(client)
                db.commit()
            
            pt = db.query(PolicyType).filter(PolicyType.company_id == company.id).first()
            if not pt:
                pt = PolicyType(company_id=company.id, name="Test Auto", code="AUTO")
                db.add(pt)
                db.commit()
                
            policy = db.query(Policy).filter(Policy.company_id == company.id).first()
            if not policy:
                policy = Policy(
                    company_id=company.id,
                    client_id=client.id,
                    policy_type_id=pt.id,
                    policy_number=f"POL-{uuid.uuid4().hex[:6]}",
                    premium_amount=Decimal("1000"),
                    coverage_amount=Decimal("10000"),
                    status='active',
                    start_date=date.today(),
                    end_date=date.today()
                )
                db.add(policy)
                db.commit()
                
            claim = Claim(
                claim_number=f"CLM-{uuid.uuid4().hex[:6]}",
                policy_id=policy.id,
                client_id=client.id,
                company_id=company.id,
                incident_date=date.today(),
                incident_description="Test accident",
                claim_amount=Decimal("5000"),
                status='submitted'
            )
            db.add(claim)
            db.commit()
            print(f"Dummy claim created: {claim.claim_number}")

        print(f"Testing for Claim: {claim.claim_number}")
        
        # 2. Identify Subrogation Potential
        recovery_service = RecoveryService(db)
        print("Creating Subrogation record...")
        recovery = recovery_service.create_recovery_record(
            claim_id=claim.id,
            recovery_type='subrogation',
            estimated_amount=Decimal("3500.00"),
            notes="At-fault third party identified. Initiating contact with their insurer."
        )
        
        print(f"Recovery Record: {recovery.id}, Status: {recovery.status}")
        
        # 3. Finalize Recovery
        print("\nFinalizing Recovery (Money collected)...")
        finalized = recovery_service.finalize_recovery(
            recovery_id=recovery.id,
            recovered_amount=Decimal("3200.00"),
            costs=Decimal("200.00")
        )
        
        print(f"Final Status: {finalized.status}")
        print(f"Amount Recovered: {finalized.actual_recovered_amount}")
        print(f"Recovery Costs: {finalized.recovery_costs}")
        
        if finalized.status == 'recovered' and finalized.actual_recovered_amount == Decimal("3200.00"):
            print("\nSUCCESS: Subrogation flow verified.")
        else:
            print("\nFAILURE: Recovery state mismatch.")

    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(verify_claim_recovery_flow())
