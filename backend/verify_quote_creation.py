import requests
import json
import sys
import os

# Ensure we can import app modules
sys.path.append(os.getcwd())

from app.core.database import SessionLocal
from app.models.user import User
from app.models.client import Client
from app.models.premium_policy import PremiumPolicyType
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

def get_test_data():
    db = SessionLocal()
    try:
        client = db.query(Client).first()
        policy = db.query(PremiumPolicyType).first()
        
        if not client or not policy:
            print("Missing client or policy data!")
            return None, None
            
        return str(client.id), str(policy.id)
    finally:
        db.close()

def test_create_quote():
    token = get_test_token()
    if not token:
        return

    client_id, policy_id = get_test_data()
    if not client_id or not policy_id:
        print("Cannot proceed without test data.")
        return

    print(f"Testing Create Quote with Auth at {BASE_URL}/quotes/ ...")
    print(f"Client ID: {client_id}")
    print(f"Policy ID: {policy_id}")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Origin": "http://localhost:3000"
    }

    payload = {
        "client_id": client_id,
        "policy_type_id": policy_id,
        "coverage_amount": 1000000,
        "premium_frequency": "annual",
        "duration_months": 12,
        "discount_percent": 0,
        "details": {
            "risk_factors": {"age": 30}
        }
    }
    
    try:
        response = requests.post(f"{BASE_URL}/quotes/", json=payload, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    test_create_quote()
