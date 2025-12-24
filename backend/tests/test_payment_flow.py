import requests
import json
from datetime import datetime, date, timedelta
import uuid

# Configuration
BASE_URL = "http://127.0.0.1:8000/api/v1"
EMAIL = "admin@demoinsurance.com"
PASSWORD = "Admin123!"

def print_result(step, result):
    print(f"\n{'='*20} {step} {'='*20}")
    print(json.dumps(result, indent=2, default=str))

def main():
    session = requests.Session()
    
    # 1. Login
    print("\n[1] Logging in...")
    try:
        login_resp = session.post(f"{BASE_URL}/auth/login", json={
            "email": EMAIL,
            "password": PASSWORD
        })
        login_resp.raise_for_status()
        token = login_resp.json()["access_token"]
        session.headers.update({"Authorization": f"Bearer {token}"})
        print("Login successful.")
    except Exception as e:
        print(f"Login failed: {e}")
        return

    # 2. Get User Info (Company ID)
    print("\n[2] Getting user info...")
    me_resp = session.get(f"{BASE_URL}/auth/me")
    me_resp.raise_for_status()
    user_info = me_resp.json()
    company_id = user_info["company_id"]
    print(f"Company ID: {company_id}")

    # 3. Find a Policy or Create one
    # For simplicity, let's try to get a policy from the list
    print("\n[3] Getting a Policy...")
    policies_resp = session.get(f"{BASE_URL}/policies/")
    policies_resp.raise_for_status()
    policies = policies_resp.json().get("policies", [])
    
    policy_id = None
    if policies:
        policy = policies[0]
        policy_id = policy['id']
        print(f"Using existing policy: {policy_id} ({policy['policy_number']})")
    else:
        print("No policies found. Please run test_policy_flow.py first to generate data.")
        return

    # 4. Process Payment
    print("\n[4] Processing Payment...")
    payment_data = {
        "policy_id": policy_id,
        "amount": 50000,
        "payment_details": {
            "method": "cash",
            "reference_number": f"REF-{uuid.uuid4().hex[:8].upper()}"
        }
    }
    
    process_resp = session.post(f"{BASE_URL}/payments/process", json=payment_data)
    if process_resp.status_code != 201:
        print(f"Payment processing failed: {process_resp.text}")
        return
        
    payment = process_resp.json()
    payment_id = payment['id']
    print(f"Payment processed: {payment_id}")
    print_result("Processed Payment", payment)

    # 5. Verify Get Payments by Policy
    print("\n[5] Verifying Get Payments by Policy...")
    policy_payments_resp = session.get(f"{BASE_URL}/payments/policy/{policy_id}")
    if policy_payments_resp.status_code != 200:
        print(f"Failed to get payments for policy: {policy_payments_resp.text}")
    else:
        payments = policy_payments_resp.json()
        print(f"Found {len(payments)} payments for policy {policy_id}")
        
        # Verify our payment is in the list
        found = any(p['id'] == payment_id for p in payments)
        if found:
            print("SUCCESS: Payment found in policy payment list.")
        else:
            print("FAILURE: Payment NOT found in policy payment list.")
            print_result("Payment List Check", payments)

if __name__ == "__main__":
    main()
