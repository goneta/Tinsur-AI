import sys
import os
import datetime

# Set up path to import backend modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from dotenv import load_dotenv
# Explicitly load .env - critical for scripts running outside uvicorn context
backend_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
load_dotenv(os.path.join(backend_root, ".env"))
print(f"Loaded .env from {backend_root}")

from app.core.database import SessionLocal
from app.models.user import User
from app.models.client import Client
import uuid

def fix_profile():
    db = SessionLocal()
    try:
        email = "test_client@tinsur.ai"
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            print(f"User {email} not found. Please run create_test_client.py first.")
            return

        print(f"Found User: {user.id}")
        
        # Check if Client profile exists
        client = db.query(Client).filter(Client.user_id == user.id).first()
        if client:
            print("Client profile already exists.")
            return

        # Create Client profile
        new_client = Client(
            company_id=user.company_id,
            user_id=user.id,
            client_type="individual",
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            phone=user.phone,
            # Initialize with empty/default risk data so agent asks for it OR defaults it
            date_of_birth=datetime.date(1995, 1, 1), # Roughly 30 years old
            accident_count=0,
            no_claims_years=0,
            driving_license_years=5
        )
        
        # Update user role to be 'client' so the Agent finds it in check
        user.role = "client"
        
        db.add(new_client)
        db.commit()
        print(f"Successfully created Client profile for {email} and set role to 'client'.")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_profile()
