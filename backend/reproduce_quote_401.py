import requests
import json
import sys

BASE_URL = "http://127.0.0.1:8000/api/v1"

def login(email, password):
    print(f"Logging in as {email}...")
    try:
        response = requests.post(f"{BASE_URL}/auth/login", data={
            "username": email,
            "password": password
        })
        response.raise_for_status()
        data = response.json()
        print("Login successful.")
        return data["access_token"]
    except Exception as e:
        print(f"Login failed: {e}")
        if response.text:
            print(response.text)
        sys.exit(1)

def get_clients(token):
    print("Fetching clients...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/clients/", headers=headers)
    if response.status_code == 200:
        clients = response.json()["clients"]
        if clients:
            print(f"Found {len(clients)} clients. Using first one: {clients[0]['id']}")
            return clients[0]["id"]
    print("Failed to get clients or no clients found.")
    sys.exit(1)

def get_policy_types(token):
    print("Fetching policy types...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/policy-types/", headers=headers)
    if response.status_code == 200:
        ptypes = response.json()["policy_types"]
        if ptypes:
            print(f"Found {len(ptypes)} policy types. Using first one: {ptypes[0]['id']}")
            return ptypes[0]["id"]
    print("Failed to get policy types.")
    sys.exit(1)

def create_quote(token, client_id, policy_type_id):
    print("Creating quote...")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "client_id": client_id,
        "policy_type_id": policy_type_id,
        "coverage_amount": 5000000,
        "premium_frequency": "annual",
        "duration_months": 12,
        "details": {},
        "risk_factors": {}
    }
    
    # IMPORTANT: Testing the slash issue
    # We try WITH trailing slash first
    url = f"{BASE_URL}/quotes/"
    print(f"POSTing to {url}")
    
    response = requests.post(url, headers=headers, json=payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 401:
        print("!!! 401 UNAUTHORIZED !!!")
    elif response.status_code == 201:
        print("SUCCESS: Quote created.")
    else:
        print("Failed with other error.")

if __name__ == "__main__":
    # You might need to adjust these credentials
    email = "admin@tinsur.ai" 
    password = "admin" 
    
    token = login(email, password)
    client_id = get_clients(token)
    policy_type_id = get_policy_types(token)
    
    create_quote(token, client_id, policy_type_id)
