import requests
import sys

BASE_URL = "http://127.0.0.1:8000/api/v1"
EMAIL = "admin@demoinsurance.com"
PASSWORD = "Password123!" 

def login():
    print(f"1. Logging in as {EMAIL}...")
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json={
            "email": EMAIL,
            "password": PASSWORD
        })
        if response.status_code == 200:
            token = response.json()["access_token"]
            print(f"   Login SUCCESS. Token received (len={len(token)})")
            return token
        else:
            print(f"   Login FAILED: {response.text}")
            sys.exit(1)
    except Exception as e:
        print(f"   Login ERROR: {e}")
        sys.exit(1)

def create_quote(token):
    print("2. Creating Quote via Authenticated Endpoint...")
    
    # Needs a client ID + Policy Type ID.
    # We can fetch them or hardcode if we know them from previous runs.
    # Let's fetch client first to be safe.
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2a. Fetch Clients
    resp_clients = requests.get(f"{BASE_URL}/clients/", headers=headers, params={"limit": 1})
    if resp_clients.status_code != 200:
        print(f"   Fetch Clients Failed: {resp_clients.text}")
        sys.exit(1)
    
    # The endpoint returns a direct List[ClientResponse], not a dict with "clients" key
    clients = resp_clients.json()
    if not clients:
        print("   No clients found in DB.")
        sys.exit(1)
        
    client_id = clients[0]["id"]
    print(f"   Using Client ID: {client_id}")
    
    # 2b. Fetch Policy Types
    resp_pt = requests.get(f"{BASE_URL}/policy-types/", headers=headers)
    ptypes = resp_pt.json()["policy_types"]
    if not ptypes:
         print("   No policy types found.")
         sys.exit(1)
    
    policy_type_id = ptypes[0]["id"]
    print(f"   Using Policy Type ID: {policy_type_id}")
    
    # 2c. Create Quote
    payload = {
        "client_id": client_id,
        "policy_type_id": policy_type_id,
        "coverage_amount": 10000000,
        "premium_frequency": "annual",
        "duration_months": 12,
        "discount_percent": 0,
        "details": {"test": "full_flow_verification"},
        "financial_overrides": {}
    }
    
    # IMPORTANT: Use Correct URL with slash
    url = f"{BASE_URL}/quotes/" 
    print(f"   POSTing to {url}")
    
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 201:
        data = response.json()
        print("   SUCCESS! Quote Created.")
        print(f"   Quote Number: {data['quote_number']}")
        print(f"   Created By (User ID): {data['created_by']}")
        print(f"   Status: {data['status']}")
    else:
        print(f"   FAILURE ({response.status_code}): {response.text}")

def create_quote_hybrid(client_id, policy_type_id, user_id):
    print("\n3. Testing Hybrid Auth (Simulating Stale Token)...")
    
    # Use a JUNK token to force 401/None user in backend
    headers = {"Authorization": "Bearer iamastaletoken"}
    
    payload = {
        "client_id": client_id,
        "policy_type_id": policy_type_id,
        "coverage_amount": 5000000,
        "premium_frequency": "monthly",
        "duration_months": 6,
        "discount_percent": 10,
        "details": {"test": "hybrid_flow_verification"},
        "financial_overrides": {},
        "created_by": user_id # Explicitly sending ID
    }
    
    url = f"{BASE_URL}/quotes/"
    print(f"   POSTing to {url} with INVALID Token but Valid Payload ID...")
    
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 201:
        data = response.json()
        print("   SUCCESS! Hybrid Quote Created.")
        print(f"   Quote Number: {data['quote_number']}")
        print(f"   Created By (User ID): {data['created_by']}")
        if data['created_by'] == user_id:
            print("   VERIFIED: Attribution matches payload ID.")
        else:
            print("   WARNING: Attribution mismatch!")
    else:
        print(f"   FAILURE ({response.status_code}): {response.text}")

if __name__ == "__main__":
    token = login()
    # We need to extract IDs to reuse in hybrid test
    # Let's just run the auth one, capturing IDs
    # ... actually let's just create a new script or hack this one.
    # Hack: I'll just run valid first, if it works, good.
    create_quote(token)
    
    # Hardcoded IDs from previous successful run output to test hybrid quickly?
    # No, let's fetch them in a clean way if we really want to be robust. 
    # But for now, just verifying the Valid Flow works (fixing the crash) is P0.
    # The hybrid flow test is P1.
    pass
