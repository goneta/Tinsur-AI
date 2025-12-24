import sys
import os
import uuid

# Ensure we can import app modules
sys.path.append(os.getcwd())

from app.core.database import SessionLocal
from app.models.user import User
from app.models.company import Company

def fix_admin_company():
    db = SessionLocal()
    try:
        user = db.query(User).first()
        if not user:
            print("No user found.")
            return

        print(f"User found: {user.email}, Company ID: {user.company_id}")

        if user.company_id:
            print("User already has a company. Verifying it exists...")
            company = db.query(Company).filter(Company.id == user.company_id).first()
            if company:
                print(f"Company exists: {company.name}")
                return
            else:
                print("Company ID is invalid (company deleted?). Fixing...")

        # Find or create company
        company = db.query(Company).first()
        if not company:
            print("No company found. Creating Default Company...")
            company = Company(
                id=uuid.uuid4(),
                name="Default Insurance Co",
                email="contact@default.com",
                phone="0000000000",
                address="123 Default St",
                # Add other required fields if any
            )
            db.add(company)
            db.commit()
            db.refresh(company)
            print(f"Created company: {company.id}")

        user.company_id = company.id
        db.add(user)
        db.commit()
        print(f"Linked user {user.email} to company {company.name} ({company.id})")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    fix_admin_company()
