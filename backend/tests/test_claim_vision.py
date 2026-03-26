"""
Integration test for AI Damage Assessment (Vision).
"""
import sys
import os
import asyncio
from uuid import UUID
from decimal import Decimal

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.core.database import SessionLocal
from app.models.claim import Claim
from app.models.user import User
from app.services.claim_service import ClaimService

async def test_claim_vision():
    db = SessionLocal()
    try:
        # 1. Get a test claim with evidence
        claims = db.query(Claim).all()
        claim = next((c for c in claims if c.evidence_files), None)
        if not claim:
            # Create a mock claim for testing if none exists
            print("No claim with evidence found. Creating a mock claim...")
            from app.models.policy import Policy
            policy = db.query(Policy).first()
            user = db.query(User).first()
            
            from app.schemas.claim import ClaimCreate
            service = ClaimService(db)
            claim_data = ClaimCreate(
                policy_id=policy.id,
                company_id=policy.company_id,
                incident_date=policy.start_date,
                incident_description="Test vehicle collision for AI vision.",
                claim_amount=1500000,
                evidence_files=["https://example.com/car-damage.jpg"],
                created_by=user.id
            )
            claim = service.create_claim(claim_data)
        
        print(f"Testing claim: {claim.claim_number}")
        print(f"Evidence files: {claim.evidence_files}")

        # 2. Setup service
        service = ClaimService(db)
        user = db.query(User).first()

        # 3. Trigger AI Analysis
        print("Running AI Vision analysis...")
        results = await service.analyze_claim_damage(claim.id, user.id)
        
        print(f"AI Results: {results}")

        # 4. Verify results
        if "error" in results:
            print(f"FAILURE: AI analysis error: {results['error']}")
            return

        db.refresh(claim)
        if claim.ai_assessment:
            print("SUCCESS: Claim updated with AI assessment.")
            print(f"Severity: {claim.ai_assessment.get('severity')}")
            print(f"Suggested Estimate: {claim.ai_assessment.get('suggested_estimate')} XOF")
        else:
            print("FAILURE: Claim ai_assessment field is still empty.")

    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(test_claim_vision())
