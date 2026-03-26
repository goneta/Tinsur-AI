import sys
import os
import requests
import json
from datetime import date

# Login specific URL and payload
BASE_URL = "http://localhost:8000/api/v1"
LOGIN_URL = f"{BASE_URL}/auth/login"
CLIENTS_URL = f"{BASE_URL}/clients/"

def test_create_client():
    # 1. Login to get token
    print(f"Logging in to {LOGIN_URL}...")
    try:
        login_payload = {
            "email": "admin@demoinsurance.com",
            "password": "admin"
        }
        response = requests.post(LOGIN_URL, json=login_payload)
        
        if response.status_code != 200:
            print(f"Login failed: {response.status_code} {response.text}")
            return

        token = response.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        print("Login successful. Token obtained.")

        # 2. Create Client
        print(f"Creating client at {CLIENTS_URL}...")
        client_payload = {
            "client_type": "individual",
            "first_name": "Test",
            "last_name": "User",
            "email": "test.user.network.error@example.com",
            "phone": "1234567890",
            "country": "France",
            "risk_profile": "medium",
            "kyc_status": "pending",
            "accident_count": 0,
            "no_claims_years": 0,
            "driving_license_years": 0
            # Created_by and company_id are handled by backend or optionally passed
        }
        
        response = requests.post(CLIENTS_URL, json=client_payload, headers=headers)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")

        if response.status_code == 201:
            print("Client created successfully!")
        else:
            print("Client creation FAILED.")

    except requests.exceptions.ConnectionError:
        print("Connection Refused! Is the backend running?")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    test_create_client()
