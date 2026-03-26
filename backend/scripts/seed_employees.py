import sys
import os
import uuid
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.core.database import SessionLocal
from app.models.user import User
from app.models.company import Company
from app.core.security import get_password_hash
# Import all models to ensure mappers are initialized
from app.models.client import Client
from app.models.policy_type import PolicyType
from app.models.quote import Quote
from app.models.premium_policy import PremiumPolicyType
from app.models.policy_service import PolicyService
from app.models.regulatory import IFRS17Group
from app.models.pos_location import POSLocation
from app.models.endorsement import Endorsement
from app.models.claim import Claim
from app.models.co_insurance import CoInsuranceShare

def seed_employees():
    db = SessionLocal()
    try:
        print("Seeding Employees...")
        
        # Get Company
        company = db.query(Company).filter(Company.subdomain == "demoinsurance.com").first()
        if not company:
            print("Company not found! Run seed_test_data.py first.")
            return

        employees_data = [
            {
                "email": "agent.smith@demoinsurance.com",
                "first_name": "John",
                "last_name": "Smith",
                "role": "agent",
                "password": "agent"
            },
            {
                "email": "sarah.connor@demoinsurance.com",
                "first_name": "Sarah",
                "last_name": "Connor",
                "role": "manager",
                "password": "manager"
            },
            {
                "email": "neo.anderson@demoinsurance.com",
                "first_name": "Neo",
                "last_name": "Anderson",
                "role": "agent",
                "password": "neo"
            }
        ]

        for emp_data in employees_data:
            existing_user = db.query(User).filter(User.email == emp_data["email"]).first()
            if not existing_user:
                new_user = User(
                    company_id=company.id,
                    email=emp_data["email"],
                    first_name=emp_data["first_name"],
                    last_name=emp_data["last_name"],
                    password_hash=get_password_hash(emp_data["password"]),
                    role=emp_data["role"],
                    is_active=True
                )
                db.add(new_user)
                print(f"Created Employee: {emp_data['email']}")
            else:
                print(f"Employee already exists: {emp_data['email']}")
        
        db.commit()
        print("Employee Seeding Complete.")

    except Exception as e:
        print(f"Error seeding employees: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_employees()
