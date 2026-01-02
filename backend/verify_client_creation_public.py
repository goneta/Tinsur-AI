import requests
import sys
import os

# Ensure we can import app modules
sys.path.append(os.getcwd())
from app.core.database import SessionLocal
from app.models.company import Company

BASE_URL = "http://localhost:8000/api/v1"

def get_company_id():
    db = SessionLocal()
    try:
        company = db.query(Company).first()
        if company:
            return str(company.id)
        return None
    finally:
        db.close()

def test_public_create_client():
    company_id = get_company_id()
    if not company_id:
        print("No company found to test public submission.")
        return

    print(f"Testing Public Create Client (No Auth) at {BASE_URL}/clients/ ...")
    
    # Headers WITHOUT Authorization
    headers = {
        "Content-Type": "application/json",
        "Origin": "http://localhost:3000"
    }

    import random
    import string
    random_str = ''.join(random.choices(string.ascii_lowercase, k=6))

    payload = {
        "client_type": "individual",
        "first_name": "Public",
        "last_name": "User",
        "email": f"public.user.{random_str}@example.com",
        "phone": "+2250102030405",
        "country": "Côte d'Ivoire",
        "company_id": company_id  # Explicitly providing company_id
    }
    
    try:
        response = requests.post(f"{BASE_URL}/clients/", json=payload, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    test_public_create_client()
