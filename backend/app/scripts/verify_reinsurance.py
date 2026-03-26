
import sys
import os
from decimal import Decimal
import uuid
from datetime import date
import asyncio

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.core.database import SessionLocal, engine, Base
from app.models.reinsurance import ReinsuranceTreaty, ReinsuranceCession, ReinsuranceRecovery
from app.models.policy import Policy
from app.models.claim import Claim
from app.services.reinsurance_service import ReinsuranceService
from app.services.claim_service import ClaimService
from app.schemas.claim import ClaimUpdate

async def verify_reinsurance_flow():
    print("Ensuring Reinsurance tables exist...")
    Base.metadata.create_all(bind=engine)
    
    print("Verifying Reinsurance Management Flow...")
    db = SessionLocal()
    try:
        policy = db.query(Policy).first()
        if not policy:
            print("No policy found for testing.")
            return

        # Use a random number for the treaty to avoid uniqueness/cleanup issues
        treaty_no = f"RE-TEST-{uuid.uuid4().hex[:6]}"
        treaty = ReinsuranceTreaty(
            company_id=policy.company_id,
            reinsurer_name="Global Re Inc",
            treaty_number=treaty_no,
            share_percentage=Decimal("20.00"),
            commission_percentage=Decimal("5.00"),
            treaty_type="quota_share",
            start_date=date(2025, 1, 1),
            end_date=date(2026, 12, 31),
            status="active"
        )
        db.add(treaty)
        db.commit()
        print(f"Treaty Created: {treaty_no} (20% Share)")

        # 2. Trigger Cession
        re_service = ReinsuranceService(db)
        print(f"Processing Cession for Policy: {policy.policy_number}")
        re_service.process_policy_cessions(policy)
        
        cession = db.query(ReinsuranceCession).filter(
            ReinsuranceCession.policy_id == policy.id,
            ReinsuranceCession.treaty_id == treaty.id
        ).first()
        
        if cession:
            print(f"SUCCESS: Cession Recorded. Ceded Premium: {cession.ceded_premium}")
        else:
            print("FAILURE: No cession recorded.")

        # 3. Trigger Recovery
        claim = db.query(Claim).filter(Claim.policy_id == policy.id).first()
        if not claim:
            claim = Claim(
                claim_number=f"CLM-RE-{uuid.uuid4().hex[:4]}",
                policy_id=policy.id,
                client_id=policy.client_id,
                company_id=policy.company_id,
                incident_date=date.today(),
                incident_description="Test reinsurance recovery description",
                incident_location="Test Office",
                claim_amount=Decimal("10000.00"),
                status="submitted"
            )
            db.add(claim)
            db.commit()
            print(f"Mock Claim Created: {claim.claim_number}")

        print("Approving claim to trigger recovery...")
        claim_service = ClaimService(db)
        update = ClaimUpdate(status="approved", approved_amount=Decimal("10000.00"))
        await claim_service.update_claim(claim.id, update)
        
        recovery = db.query(ReinsuranceRecovery).filter(
            ReinsuranceRecovery.claim_id == claim.id,
            ReinsuranceRecovery.treaty_id == treaty.id
        ).first()
        
        if recovery:
            print(f"SUCCESS: Recovery Recorded. Amount: {recovery.recoverable_amount}")
        else:
            print("FAILURE: No recovery recorded.")

    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(verify_reinsurance_flow())
