import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from app.core.database import SessionLocal
from app.models.user import User
from app.core.security import verify_password

def verify():
    db = SessionLocal()
    try:
        # Check Admin
        admin = db.query(User).filter(User.email == "admin@demoinsurance.com").first()
        if admin:
            print(f"Admin found: {admin.email}")
            if verify_password("Admin123!", admin.password_hash):
                print("SUCCESS: Admin password verified!")
            else:
                print("FAILURE: Admin password mismatch!")
        else:
             print("FAILURE: Admin not found!")

        # Check Client
        client = db.query(User).filter(User.email == "test_client@tinsur.ai").first()
        if client:
             print(f"Client found: {client.email}")
             if verify_password("Client123!", client.password_hash):
                 print("SUCCESS: Client password verified!")
             else:
                 print("FAILURE: Client password mismatch!")
        else:
             print("FAILURE: Client not found!")
             
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    verify()
