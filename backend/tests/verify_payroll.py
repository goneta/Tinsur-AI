import sys
import os
import uuid
from datetime import datetime
from decimal import Decimal

# Add backend directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.database import SessionLocal
from app.models.user import User
from app.models.company import Company
from app.models.payroll import PayrollTransaction
from app.models.employee import EmployeeProfile

def verify_payroll():
    db = SessionLocal()
    try:
        # 1. Setup - Get an admin and an employee from the same company
        admin = db.query(User).filter(User.role == 'manager').first()
        if not admin:
            print("No manager found in DB. Please run create_admin.py or ensure data exists.")
            return

        print(f"Using Admin: {admin.email} (Company ID: {admin.company_id})")

        employee = db.query(User).filter(
            User.role.in_(['agent', 'receptionist']),
            User.company_id == admin.company_id
        ).first()

        if not employee:
            print(f"No employee found for company {admin.company_id}. Creating one...")
            employee = User(
                id=uuid.uuid4(),
                email=f"test_emp_{uuid.uuid4().hex[:4]}@example.com",
                hashed_password="hashed",
                first_name="Test",
                last_name="Employee",
                role="agent",
                company_id=admin.company_id,
                is_active=True
            )
            db.add(employee)
            db.commit()
            db.refresh(employee)
            
            # Ensure profile exists
            profile = EmployeeProfile(
                user_id=employee.id,
                base_salary=Decimal("250000.00"),
                currency="XOF",
                payment_method="bank_transfer"
            )
            db.add(profile)
            db.commit()

        print(f"Using Employee: {employee.email}")

        # 2. Simulate "Pay Now" logic
        print("\nProcessing 'Pay Now' simulation...")
        tx_id = uuid.uuid4()
        payment_month = datetime.now().strftime("%B %Y")
        
        new_transaction = PayrollTransaction(
            id=tx_id,
            employee_id=employee.id,
            company_id=admin.company_id,
            amount=Decimal("250000.00"),
            currency="XOF",
            payment_method="bank_transfer",
            status='paid',
            description="Salary Payment - Verification Test",
            payment_month=payment_month,
            reference_number=f"TX-{uuid.uuid4().hex[:8].upper()}",
            processed_by=admin.id,
            payment_date=datetime.utcnow()
        )
        
        db.add(new_transaction)
        db.commit()
        print(f"Transaction {tx_id} created successfully.")

        # 3. Verify record creation
        verified_tx = db.query(PayrollTransaction).filter(PayrollTransaction.id == tx_id).first()
        if verified_tx:
            print(f"VERIFICATION SUCCESS: Transaction found in database with status '{verified_tx.status}'.")
        else:
            print("VERIFICATION FAILURE: Transaction not found in database.")
            return

        # 4. Verify History Table Logic (Retrieve all transactions for company)
        print("\nChecking history table logic...")
        history = db.query(PayrollTransaction).filter(PayrollTransaction.company_id == admin.company_id).order_by(PayrollTransaction.payment_date.desc()).all()
        
        found = False
        for h in history:
            if h.id == tx_id:
                found = True
                print(f"SUCCESS: Newest transaction {h.id} appears in history list.")
                break
        
        if not found:
            print("FAILURE: New transaction did not appear in history.")

    except Exception as e:
        print(f"ERROR: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    verify_payroll()
