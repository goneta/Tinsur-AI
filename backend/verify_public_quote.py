import requests
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Database connection
SQLALCHEMY_DATABASE_URL = "sqlite:///./insurance.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

BASE_URL = "http://127.0.0.1:8000/api/v1"

def get_test_data():
    db = SessionLocal()
    try:
        # Get a client
        result = db.execute(text("SELECT id, company_id FROM clients LIMIT 1"))
        client = result.fetchone()
        
        # Get a policy type
        result_pt = db.execute(text("SELECT id FROM policy_types LIMIT 1"))
        pt = result_pt.fetchone()
        
        if not client or not pt:
            print("Error: No client or policy type found in DB.")
            sys.exit(1)
            
        return client[0], client[1], pt[0]
    finally:
        db.close()

def test_public_create_quote(client_id, policy_type_id):
    print(f"Testing Public Quote Creation...")
    print(f"Client ID: {client_id}")
    print(f"Policy Type ID: {policy_type_id}")
    
    # Payload matching QuoteCreate schema
    payload = {
        "client_id": str(client_id),
        "policy_type_id": str(policy_type_id),
        "coverage_amount": 5000000,
        "premium_frequency": "annual",
        "duration_months": 12,
        "discount_percent": 0,
        "details": {"test": "data"},
        "financial_overrides": {}
    }
    
    # NO AUTH HEADERS
    headers = {
        "Content-Type": "application/json"
    }
    
    url = f"{BASE_URL}/quotes/"
    print(f"POSTing to {url}")
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code in [200, 201]:
            print("SUCCESS: Quote created without auth!")
        else:
            print("FAILURE: Request failed.")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    client_id, company_id, policy_type_id = get_test_data()
    test_public_create_quote(client_id, policy_type_id)
