import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_create_employee():
    print(f"Testing Create Employee at {BASE_URL}/employees/ ...")
    
    # login first to get token (if needed, but assuming dev mode might allow open access or we have a test user)
    # Actually, let's try to create a standard user first if auth is required.
    # For now, let's assume we can hit it if we had a token. 
    # But wait, the frontend uses a token. 
    # I'll just check if the endpoint accepts connections, even if 401.
    
    payload = {
        "email": "test.employee.latest@example.com",
        "password": "Password123!",
        "first_name": "Test",
        "last_name": "Employee",
        "role": "agent",
        "payment_method": "bank_transfer",
        "created_by": None,
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
        # We expect 401 if not auth, but NOT 'Network Error' (connection refused).
        response = requests.post(f"{BASE_URL}/employees/", json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:500]}")
        
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    test_create_employee()
