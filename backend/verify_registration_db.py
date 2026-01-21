from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from backend.app.core.database import SessionLocal
from backend.app.models.user import User
from backend.app.models.client import Client
from backend.app.models.client_details import ClientDriver

def check_registration(email):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            print(f"User {email} not found")
            return
        
        print(f"User found: ID={user.id}, Email={user.email}, Type={user.user_type}")
        
        client = db.query(Client).filter(Client.user_id == user.id).first()
        if not client:
            print("Client record NOT found for this user")
            return
            
        print(f"Client found: ID={client.id}, Name={client.first_name} {client.last_name}, Type={client.client_type}")
        
        drivers = db.query(ClientDriver).filter(ClientDriver.client_id == client.id).all()
        print(f"Drivers found: {len(drivers)}")
        for d in drivers:
            print(f"  - Driver: ID={d.id}, Name={d.first_name} {d.last_name}, Main={d.is_main_driver}, License={d.license_number}")
            
    finally:
        db.close()

if __name__ == "__main__":
    email = "johndoe_test_unique@example.com"
    check_registration(email)
