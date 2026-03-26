import requests
import json
import sys
import os

# Ensure we can import app modules
sys.path.append(os.getcwd())

from app.core.database import SessionLocal
from app.models.user import User
from app.core.security import create_access_token
from app.core.config import settings

BASE_URL = "http://localhost:8000/api/v1"

def get_test_token():
    db = SessionLocal()
    try:
        user = db.query(User).first()
        if not user:
            print("No user found! Cannot test auth.")
            return None
        return create_access_token({"sub": str(user.id)})
    finally:
        db.close()

def test_create_employee():
    token = get_test_token()
    if not token:
        return

    print(f"Testing Create Employee with Auth at {BASE_URL}/employees/ ...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Origin": "http://localhost:3000"
    }

    # MATCHING FRONTEND PAYLOAD EXACTLY
    # Note: frontend sends `null` for `created_by` if sanitized, or `undefined` (omitted).
    # If the Zod schema says `created_by: z.string().optional()`, it sends nothing if undefined.
    # But let's try sending explicit null to see if Pydantic chokes.
    
    import random
    import string
    random_str = ''.join(random.choices(string.ascii_lowercase, k=6))
    
    payload = {
        "email": f"test.employee.{random_str}@example.com",
        "password": "Password123!",
        "first_name": "Crash",
        "last_name": "Check",
        "role": "agent",
        # "company_id": ... # Let backend infer it from Admin
        "profile": {
            "payment_method": "bank_transfer",
            "base_salary": 500000,
            "currency": "XOF",
            "department": "Sales",
            "job_title": "Agent",
            "iban": "FR761234567890",
            "swift_bic": "XXXXXXXX"
        }
    }
    
    try:
        response = requests.post(f"{BASE_URL}/employees/", json=payload, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    test_create_employee()
