import requests
import json
import sys
import os

# Ensure we can import app modules
sys.path.append(os.getcwd())

from app.core.database import SessionLocal
from app.models.user import User
from app.core.security import create_access_token

BASE_URL = "http://localhost:8000/api/v1"

def get_test_token():
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email.like("%admin%")).first()
        if not user:
             user = db.query(User).first()
        
        if not user:
            print("No user found! Cannot test auth.")
            return None
        print(f"Using user: {user.email} (ID: {user.id})")
        return create_access_token({
            "sub": str(user.id),
            "email": user.email,
            "role": user.role,
            "company_id": str(user.company_id) if user.company_id else None
        })
    finally:
        db.close()

def test_create_client():
    token = get_test_token()
    if not token:
        return

    print(f"Testing Create Client with Auth at {BASE_URL}/clients/ ...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Origin": "http://localhost:3000"
    }

    payload = {
        "client_type": "individual",
        "first_name": "Test",
        "last_name": "Verif",
        "email": "test.verif@example.com",
        "phone": "+2250102030405",
        "country": "Côte d'Ivoire",
         "risk_profile": "medium",
         "kyc_status": "pending"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/clients/", json=payload, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    test_create_client()
