import sys
import os

# Ensure backend directory is in path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.user import User
from app.models.company import Company
from app.core.security import get_password_hash
import uuid

# Database setup
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_test_users():
    db = SessionLocal()
    try:
        # 1. Ensure a Company exists
        company = db.query(Company).filter(Company.name == "Test Company").first()
        if not company:
            company = Company(
                name="Test Company",
                subdomain="test-company",
                email="info@testcompany.com",
                country="USA"
            )
            db.add(company)
            db.commit()
            db.refresh(company)
            print(f"Created Test Company: {company.id}")
        else:
            print(f"Using Test Company: {company.id}")

        # 2. Define Users to Create
        users_to_create = [
            {
                "email": "client@example.com",
                "password": "Password123!",
                "role": "client",
                "first_name": "Test",
                "last_name": "Client"
            },
            {
                "email": "agent@example.com",
                "password": "Password123!",
                "role": "agent",
                "first_name": "Test",
                "last_name": "Agent"
            },
            {
                "email": "employee@example.com",
                "password": "Password123!",
                "role": "agent", # Using 'agent' as employee proxy
                "first_name": "Test",
                "last_name": "Employee"
            },
            {
                "email": "manager@example.com",
                "password": "Password123!",
                "role": "manager",
                "first_name": "Test",
                "last_name": "Manager"
            }
        ]

        for u_data in users_to_create:
            existing_user = db.query(User).filter(User.email == u_data["email"]).first()
            if not existing_user:
                new_user = User(
                    email=u_data["email"],
                    password_hash=get_password_hash(u_data["password"]),
                    role=u_data["role"],
                    first_name=u_data["first_name"],
                    last_name=u_data["last_name"],
                    company_id=company.id,
                    is_active=True,
                    is_verified=True
                )
                db.add(new_user)
                print(f"Created User: {u_data['email']} ({u_data['role']})")
            else:
                print(f"User already exists: {u_data['email']}")

        db.commit()
        print("Test users creation complete.")

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_test_users()
