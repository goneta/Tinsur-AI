
import requests
import json
import sys

BASE_URL = "http://localhost:8000/api/v1"

def test_quote_creation():
    # 1. Login to get token
    print("Logging in...")
    login_resp = requests.post(f"{BASE_URL}/auth/login", json={"email": "admin@demoinsurance.com", "password": "Password123!"})
    if login_resp.status_code != 200:
        print(f"Login Failed: {login_resp.text}")
        return
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Get Client
    print("Fetching Clients...")
    clients_resp = requests.get(f"{BASE_URL}/clients/", headers=headers)
    if clients_resp.status_code != 200:
        print(f"Clients Fetch Failed: {clients_resp.text}")
        return
    clients = clients_resp.json()
    if not clients:
        print("No clients found. Seed DB first.")
        return
    client_id = clients[0]["id"]
    print(f"Using Client ID: {client_id}")

    # 3. Get Policy Type from existing quotes
    print("Fetching Policy Type from existing quotes...")
    q_resp = requests.get(f"{BASE_URL}/quotes/", headers=headers, params={"limit": 50})
    policy_type_id = None
    if q_resp.status_code == 200:
        data = q_resp.json()
        # Handle new format {quotes: [], total: ...}
        quotes = data if isinstance(data, list) else data.get("quotes", [])
        if quotes:
             policy_type_id = quotes[0]['policy_type_id']
             print(f"Using Policy Type ID from Quote: {policy_type_id}")
    
    if not policy_type_id:
        print("Could not find any existing quotes to steal Policy Type ID from. Script might fail.")
        # Fallback to a hardcoded one if known or Abort
        # Let's hope seeded data exists.
        return

    # 4. Create Quote
    print("Creating Quote...")
    payload = {
        "client_id": client_id,
        "policy_type_id": policy_type_id,
        "coverage_amount": 5000000,
        "premium_frequency": "annual",
        "duration_months": 12,
        "discount_percent": 0,
        "details": {
            "driver_age": 30,
            "vehicle_age": 2
        }
    }
    
    resp = requests.post(f"{BASE_URL}/quotes/", headers=headers, json=payload)
    print(f"Response Code: {resp.status_code}")
    print(f"Response Body: {resp.text}")

if __name__ == "__main__":
    test_quote_creation()
