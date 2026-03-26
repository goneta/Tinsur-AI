import requests
import uuid
import time

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
ADMIN_EMAIL = "admin@demoinsurance.com"
ADMIN_PASSWORD = "Admin123!"

def test_sales_attribution_and_commissions():
    print("\n--- Testing Sales Attribution and Commissions ---")
    
    # 1. Login
    login_response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    if login_response.status_code != 200:
        print(f"Login failed: {login_response.status_code} - {login_response.text}")
        exit(1)
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("LoggedIn.")

    # Get current user to use as agent
    user_me = requests.get(f"{BASE_URL}/auth/me", headers=headers).json()
    my_id = user_me["id"]
    company_id = user_me["company_id"]

    pt_response = requests.get(f"{BASE_URL}/policy-types/", headers=headers)
    pt_data = pt_response.json()
    if isinstance(pt_data, dict) and "policy_types" in pt_data:
        policy_types = pt_data["policy_types"]
    else:
        policy_types = pt_data
        
    if not policy_types:
        print("No policy types found. Creating one...")
        # create a dummy policy type if needed or just fail
        exit(1)
    
    policy_type = policy_types[0]
    
    # 3. Create a client
    client_data = {
        "client_type": "individual",
        "first_name": "Sales",
        "last_name": "Test",
        "email": f"sales_test_{uuid.uuid4().hex[:8]}@example.com",
        "phone": "+22501020304"
    }
    client_response = requests.post(f"{BASE_URL}/clients/", json=client_data, headers=headers).json()
    client_id = client_response.get("id") or client_response.get("client", {}).get("id")
    if not client_id:
        print(f"Failed to get client ID: {client_response}")
        exit(1)

    # 4. Create a policy with Sales Agent ID
    policy_data = {
        "client_id": client_id,
        "policy_type_id": policy_type["id"],
        "policy_number": f"POL-SALES-{int(time.time())}",
        "start_date": "2024-01-01",
        "end_date": "2024-12-31",
        "premium_amount": 500000,
        "status": "active",
        "sales_agent_id": my_id # Attribute to myself
    }
    policy_response = requests.post(f"{BASE_URL}/policies/", json=policy_data, headers=headers).json()
    policy_id = policy_response.get("id") or policy_response.get("policy", {}).get("id")
    
    if not policy_id:
        print(f"Failed to get policy ID: {policy_response}")
        exit(1)
        
    print(f"Policy created: {policy_id} with agent {my_id}")

    # 5. Process a payment
    payment_data = {
        "policy_id": policy_id,
        "amount": 500000,
        "payment_details": {
            "method": "cash",
            "gateway": "manual"
        }
    }
    payment = requests.post(f"{BASE_URL}/payments/process", json=payment_data, headers=headers).json()
    print(f"Payment processed: {payment['payment_number']} - Status: {payment['status']}")

    # 6. Verify Commission record
    # Wait a moment for processing if it was async (though here it's sync in process_payment)
    comm_response = requests.get(f"{BASE_URL}/commissions/?agent_id={my_id}", headers=headers)
    commissions = comm_response.json()
    
    print(f"Checking commissions for Policy ID: {policy_id}")
    print(f"Response data: {commissions}")
    found = False
    for comm in commissions:
        if isinstance(comm, dict):
            comm_policy_id = str(comm.get("policy_id"))
            target_policy_id = str(policy_id)
            if comm_policy_id == target_policy_id:
                print(f"SUCCESS: Commission found! Amount: {comm['amount']} - Status: {comm['status']}")
                found = True
                break
            else:
                print(f"Mismatch: {comm_policy_id} != {target_policy_id}")
            
    if not found:
        print("FAILURE: Commission record not created for the policy.")
        exit(1)

    print("--- Test Complete ---\n")

if __name__ == "__main__":
    test_sales_attribution_and_commissions()
