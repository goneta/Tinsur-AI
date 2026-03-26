"""
Integration test for AI Credit Top-up Flow.
"""
import sys
import os
from uuid import UUID
from decimal import Decimal

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.core.database import SessionLocal
from app.models.company import Company
from app.models.payment import Payment
from app.repositories.payment_repository import PaymentRepository
from app.services.payment_service import PaymentService

def test_topup_flow():
    db = SessionLocal()
    try:
        # 1. Get a test company
        company = db.query(Company).filter(Company.subdomain == "demo").first()
        if not company:
            print("Demo company not found. Please seed data first.")
            return

        initial_balance = company.ai_credits_balance or 0.0
        print(f"Initial balance: ${initial_balance}")

        # 2. Setup repositories and services
        payment_repo = PaymentRepository(db)
        payment_service = PaymentService(db, payment_repo)

        # 3. Create a top-up payment with Moov
        print("Initiating top-up of $30 via Moov...")
        payment = payment_service.create_payment(
            company_id=company.id,
            policy_id=None,
            client_id=None,
            amount=Decimal("30.00"),
            payment_method="mobile_money",
            payment_gateway="moov_money",
            metadata={"type": "ai_credits"}
        )
        
        print(f"Payment created: {payment.payment_number}, Status: {payment.status}")

        # 4. Simulate payment processing (pending)
        print("Processing payment...")
        payment_service.process_payment(payment.id, {"token": "test_token", "phone_number": "0123456789"})

        # 5. Verify results
        db.refresh(company)
        new_balance = company.ai_credits_balance
        print(f"New balance: ${new_balance}")

        # 6. Verify Payment Status
        db.refresh(payment)
        print(f"Final payment status: {payment.status}")
        if payment.status == 'failed':
            print(f"Failure reason: {payment.failure_reason}")

        if payment.status == 'pending' and new_balance == initial_balance:
            print("SUCCESS: Payment is pending as expected for Mobile Money.")
        elif payment.status == 'completed' and new_balance == initial_balance + 30.0:
            print("SUCCESS: Credits updated correctly.")
        else:
            print(f"FAILURE: Unexpected state. Status: {payment.status}, Balance: {new_balance}")
        
    finally:
        db.close()

if __name__ == "__main__":
    test_topup_flow()
