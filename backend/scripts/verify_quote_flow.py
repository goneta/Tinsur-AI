import requests
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8000/api/v1"
LOGIN_URL = f"{BASE_URL}/auth/login"

def login(email, password):
    payload = {"email": email, "password": password}
    response = requests.post(LOGIN_URL, json=payload)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        logger.error(f"Login failed: {response.text}")
        return None

def verify_flow():
    token = login("admin@demoinsurance.com", "admin123")
    if not token:
        print("FAIL: Could not log in")
        return

    headers = {"Authorization": f"Bearer {token}"}

    # 1. Get Prerequisites (Client, PolicyType)
    logger.info("Fetching clients...")
    res = requests.get(f"{BASE_URL}/clients/", headers=headers)
    if not res.ok or not res.json():
        logger.error("No clients found. Run seeding.")
        return
    client_id = res.json()[0]['id']

    logger.info("Fetching policy types...")
    res = requests.get(f"{BASE_URL}/premium-policy-types/types", headers=headers)
    if not res.ok: # Fallback to standard types if prem logic differs
         res = requests.get(f"{BASE_URL}/policy-types/", headers=headers)
    
    # Premium Policy Types response struct might be {premium_policy_types: []} or just []
    types_data = res.json()
    logger.info(f"Policy Types Response: {types_data}")

    if isinstance(types_data, dict):
        if 'premium_policy_types' in types_data:
            types_data = types_data['premium_policy_types']
        elif 'policy_types' in types_data:
            types_data = types_data['policy_types']
        
    if not types_data:
        logger.info("No policy types found. Creating one...")
        # Create a dummy policy type
        pt_payload = {
            "name": "Auto Standard",
            "code": "AUTO-STD",
            "description": "Standard Auto Policy",
            "company_id": "dummy" # Backend should ignore or handle
        }
        res_pt = requests.post(f"{BASE_URL}/policy-types/", json=pt_payload, headers=headers)
        if not res_pt.ok:
            logger.error(f"Failed to create policy type: {res_pt.text}")
            return
        policy_type_id = res_pt.json()['id']
        logger.info(f"Created Policy Type: {policy_type_id}")
    else:
        policy_type_id = types_data[0]['id']

    # 2. Create Quote
    logger.info("Creating Quote...")
    quote_payload = {
        "client_id": client_id,
        "policy_type_id": policy_type_id,
        "coverage_amount": 5000000,
        "premium_frequency": "annual",
        "duration_months": 12,
        "discount_percent": 0,
        "details": {"driver_age": 30}
    }
    res = requests.post(f"{BASE_URL}/quotes/", json=quote_payload, headers=headers)
    if not res.ok:
        logger.error(f"Quote creation failed: {res.text}")
        return
    quote = res.json()
    quote_id = quote['id']
    logger.info(f"Quote Created: {quote_id} (Status: {quote['status']})")

    # 3. Send Quote
    logger.info("Sending Quote...")
    res = requests.post(f"{BASE_URL}/quotes/{quote_id}/send", headers=headers)
    if not res.ok:
         logger.error(f"Send failed: {res.text}")
         return
    logger.info(f"Quote Sent. Status: {res.json()['status']}")

    # 4. Approve Quote (Should trigger Policy Creation)
    logger.info("Approving Quote...")
    res = requests.post(f"{BASE_URL}/quotes/{quote_id}/approve", headers=headers)
    if not res.ok:
        logger.error(f"Approve failed: {res.text}")
        return
    
    data = res.json()
    logger.info(f"Approve Response: {data}")
    
    if 'policy_id' in data:
        print("SUCCESS: Policy Created via Quote Approval")
    else:
        print("FAIL: Policy ID missing in response")

    # 5. Reject Flow Verification
    logger.info("Verifying Reject Flow...")
    # Create another quote
    res = requests.post(f"{BASE_URL}/quotes/", json=quote_payload, headers=headers)
    quote2_id = res.json()['id']
    requests.post(f"{BASE_URL}/quotes/{quote2_id}/send", headers=headers)
    
    res = requests.post(f"{BASE_URL}/quotes/{quote2_id}/reject", headers=headers)
    if res.ok and res.json()['status'] == 'rejected':
        print("SUCCESS: Quote Rejected successfully")
    else:
        print(f"FAIL: Quote Rejection failed: {res.text}")

    # 6. Archive Flow Verification
    logger.info("Verifying Archive Flow...")
    # Create quote -> Send -> Approve -> Archive
    res = requests.post(f"{BASE_URL}/quotes/", json=quote_payload, headers=headers)
    quote3_id = res.json()['id']
    requests.post(f"{BASE_URL}/quotes/{quote3_id}/send", headers=headers)
    requests.post(f"{BASE_URL}/quotes/{quote3_id}/approve", headers=headers)
    
    res = requests.post(f"{BASE_URL}/quotes/{quote3_id}/archive", headers=headers)
    if res.ok and res.json()['status'] == 'archived':
        print("SUCCESS: Quote Archived successfully")
    else:
        print(f"FAIL: Quote Archive failed: {res.text}")

if __name__ == "__main__":
    verify_flow()
