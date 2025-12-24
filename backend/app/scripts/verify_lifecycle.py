"""
Verification script for the core insurance lifecycle: Quote -> Policy -> Payment -> Claim.
"""
import sys
import os
from uuid import UUID
from datetime import date, timedelta
from decimal import Decimal

# Add current directory to path to allow imports from app
sys.path.append(os.getcwd())

from app.core.database import SessionLocal
from app.models.company import Company
from app.models.user import User
from app.models.client import Client
from app.models.policy_type import PolicyType
from app.models.quote import Quote
from app.models.policy import Policy
from app.models.payment import Payment
from app.models.claim import Claim
from app.models.premium_schedule import PremiumSchedule

from app.repositories.quote_repository import QuoteRepository
from app.repositories.policy_repository import PolicyRepository
from app.repositories.endorsement_repository import EndorsementRepository
from app.repositories.payment_repository import PaymentRepository
from app.repositories.premium_schedule_repository import PremiumScheduleRepository
from app.repositories.claim_repository import ClaimRepository

from app.services.quote_service import QuoteService
from app.services.policy_service import PolicyService
from app.services.payment_service import PaymentService
from app.services.premium_service import PremiumService
from app.services.claim_service import ClaimService

def verify_lifecycle():
    db = SessionLocal()
    try:
        print("--- Starting Lifecycle Verification ---")
        
        # 0. Setup: Get a test company and user
        company = db.query(Company).first()
        if not company:
            print("Error: No company found in database. Run seeding first.")
            return
        
        user = db.query(User).filter(User.company_id == company.id).first()
        if not user:
            print("Error: No user found for the company.")
            return
            
        policy_type = db.query(PolicyType).filter(PolicyType.company_id == company.id).first()
        if not policy_type:
             # Create a default one if missing
             policy_type = PolicyType(
                 name="Auto Insurance",
                 code="AUTO",
                 description="Standard auto insurance",
                 company_id=company.id
             )
             db.add(policy_type)
             db.commit()
             db.refresh(policy_type)

        print(f"Using Company: {company.name}, User: {user.email}, Policy Type: {policy_type.name}")

        # 1. Create a Client
        client = Client(
            company_id=company.id,
            client_type="individual",
            first_name="Test",
            last_name="Lifecycle",
            email="lifecycle.test@example.com",
            phone="+22501020304",
            address="Abidjan, Ivory Coast",
            user_id=user.id
        )
        db.add(client)
        db.commit()
        db.refresh(client)
        print(f"1. Client created: {client.id}")

        # 2. Create a Quote
        quote_repo = QuoteRepository(db)
        quote_service = QuoteService(quote_repo)
        
        quote = quote_service.create_quote(
            company_id=company.id,
            client_id=client.id,
            policy_type_id=policy_type.id,
            coverage_amount=Decimal("5000000"),
            risk_factors={"driver_age": 30, "accidents": 0, "vehicle_age": 2},
            premium_frequency="monthly",
            duration_months=12,
            created_by=user.id
        )
        print(f"2. Quote created: {quote.id}, Premium: {quote.final_premium}")

        # 3. Accept Quote
        quote_service.accept_quote(quote.id)
        print(f"3. Quote accepted: {quote.status}")

        # 4. Convert Quote to Policy
        policy_repo = PolicyRepository(db)
        endorsement_repo = EndorsementRepository(db)
        policy_service = PolicyService(policy_repo, quote_repo, endorsement_repo)
        
        policy = policy_service.create_from_quote(
            quote_id=quote.id,
            start_date=date.today(),
            created_by=user.id
        )
        
        if not policy:
            print("Error: Failed to convert quote to policy.")
            return
        print(f"4. Policy created: {policy.id}, Number: {policy.policy_number}")

        # 5. Verify Premium Schedule
        schedule_repo = PremiumScheduleRepository(db)
        premium_service = PremiumService(schedule_repo)
        
        # The service calls this automatically in create_policy API, 
        # but in our direct service call for create_from_quote, let's ensure it's there
        # Let's check if there are schedules
        schedules = schedule_repo.get_by_policy(policy.id)
        if not schedules:
            print("Generating payment schedule manually...")
            premium_service.generate_payment_schedule(
                company_id=company.id,
                policy_id=policy.id,
                total_premium=policy.premium_amount,
                frequency=policy.premium_frequency,
                start_date=policy.start_date,
                duration_months=12
            )
            schedules = schedule_repo.get_by_policy(policy.id)
        
        print(f"5. Premium Schedule generated: {len(schedules)} installments")
        
        # 6. Process a Payment
        payment_repo = PaymentRepository(db)
        payment_service = PaymentService(db, payment_repo)
        
        # Process the first installment
        installment = schedules[0]
        payment = payment_service.create_payment(
            company_id=company.id,
            policy_id=policy.id,
            client_id=client.id,
            amount=installment.amount,
            payment_method="mobile_money",
            payment_gateway="wave"
        )
        
        # Simulate successful processing
        processed_payment = payment_service.process_payment(
            payment_id=payment.id,
            payment_details={"status": "succeeded", "transaction_id": "TRANS-123"}
        )
        
        if processed_payment.status == "completed":
            premium_service.mark_schedule_as_paid(
                schedule_id=installment.id,
                payment_id=processed_payment.id,
                amount=installment.amount
            )
            print(f"6. Payment completed: {processed_payment.id}, Installment {installment.id} marked as paid")
        else:
            print(f"Error: Payment status is {processed_payment.status}")

        # 7. Submit a Claim
        claim_repo = ClaimRepository(db)
        claim_service = ClaimService(db)
        
        from app.schemas.claim import ClaimCreate
        claim_data = ClaimCreate(
            policy_id=policy.id,
            incident_date=date.today(),
            incident_description="Test minor accident during lifecycle verification.",
            incident_location="Abidjan Plateau",
            claim_amount=Decimal("150000"),
            company_id=company.id
        )
        
        claim = claim_service.create_claim(claim_data)
        print(f"7. Claim submitted: {claim.id}, Number: {claim.claim_number}, Status: {claim.status}")

        print("--- Lifecycle Verification Successful ---")

    except Exception as e:
        print(f"Error during verification: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    verify_lifecycle()
