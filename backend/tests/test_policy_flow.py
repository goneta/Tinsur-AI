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

    # 3. Create/Get Client
    print("\n[3] Handling Client...")
    # List clients to see if any exist, otherwise create one
    clients_resp = session.get(f"{BASE_URL}/clients/")
    clients_resp.raise_for_status()
    clients = clients_resp.json()
    
    if clients:
        client = clients[0]
        print(f"Using existing client: {client['id']}")
    else:
        print("Creating new client...")
        client_data = {
            "company_id": company_id,
            "client_type": "individual",
            "email": f"test_{uuid.uuid4().hex[:8]}@example.com",
            "phone": "+2250102030405",
            "first_name": "Test",
            "last_name": "User",
            "date_of_birth": "1990-01-01",
            "address": "123 Test St",
            "city": "Abidjan",
            "country": "Côte d'Ivoire",
            "id_number": "A123456789",
        }
        create_client_resp = session.post(f"{BASE_URL}/clients/", json=client_data)
        create_client_resp.raise_for_status()
        client = create_client_resp.json()
        print(f"Created client: {client['id']}")
    
    client_id = client['id']

    # 4. Handle Policy Type
    print("\n[4] Handling Policy Type...")
    policy_type_id = None
    
    # Try to find existing
    try:
        pt_resp = session.get(f"{BASE_URL}/policy-types/")
        if pt_resp.status_code == 200:
            types = pt_resp.json().get("policy_types", [])
            if types:
                policy_type = types[0]
                policy_type_id = policy_type['id']
                print(f"Using existing policy type: {policy_type['name']} ({policy_type_id})")
    except Exception as e:
        print(f"Failed to list policy types: {e}")

    # Create if not found
    if not policy_type_id:
        print("Creating new policy type...")
        pt_data = {
            "name": "Vehicle Insurance",
            "code": "AUTO",
            "description": "Comprehensive car insurance"
        }
        try:
            pt_create = session.post(f"{BASE_URL}/policy-types/", json=pt_data)
            if pt_create.status_code == 201:
                policy_type_id = pt_create.json()['id']
                print(f"Created policy type: {policy_type_id}")
            elif pt_create.status_code == 400:
                print("Policy type code likely exists, trying to fetch again (race condition or active filter code logic mismatch)")
                # Retry fetch
                pt_resp = session.get(f"{BASE_URL}/policy-types/")
                types = pt_resp.json().get("policy_types", [])
                if types:
                   policy_type_id = types[0]['id']
            else:
                print(f"Failed to create policy type: {pt_create.text}")
        except Exception as e:
            print(f"Error creating policy type: {e}")
            
    if not policy_type_id:
        print("CRITICAL: No policy type available. Aborting.")
        return

    # 5. Create Quote
    print("\n[5] Creating Quote...")
    quote_data = {
        "client_id": client_id,
        "policy_type_id": policy_type_id,
        "coverage_amount": 5000000,
        "premium_amount": 250000,
        "final_premium": 225000,
        "discount_percent": 10,
        "premium_frequency": "annual",
        "duration_months": 12,
        "risk_score": 10,
        "valid_until": (date.today() + timedelta(days=30)).isoformat(),
        "details": {"vehicle_make": "Toyota"}
    }
    
    create_quote_resp = session.post(f"{BASE_URL}/quotes/", json=quote_data)
    if create_quote_resp.status_code != 201:
        print(f"Quote creation failed: {create_quote_resp.text}")
        return
        
    quote = create_quote_resp.json()
    quote_id = quote['id']
    print(f"Quote created: {quote_id}")

    # 6. Convert Quote to Policy
    print("\n[6] Converting Quote to Policy...")
    # First accept quote (auto-accepted by logic or manually?)
    # The endpoint `convert` calls `accept_quote`.
    convert_data = {
        "start_date": date.today().isoformat(),
        "payment_method": "cash",
        "initial_payment_amount": 225000
    }
    convert_resp = session.post(f"{BASE_URL}/quotes/{quote_id}/convert", json=convert_data)
    if convert_resp.status_code != 201:
        print(f"Conversion failed: {convert_resp.text}")
        return
        
    conversion_result = convert_resp.json()
    policy_id = conversion_result['policy_id']
    print(f"Policy created: {policy_id}")

    # 7. Create Endorsement
    print("\n[7] Creating Endorsement...")
    endorsement_data = {
        "policy_id": policy_id,
        "endorsement_type": "coverage_change",
        "effective_date": (date.today() + timedelta(days=5)).isoformat(),
        "changes": {"coverage_amount": 6000000}, # Increase coverage
        "reason": "Client requested higher coverage",
        "premium_adjustment": 50000 # Increase premium
    }
    endorsement_resp = session.post(f"{BASE_URL}/policies/{policy_id}/endorsements", json=endorsement_data)
    if endorsement_resp.status_code != 200:
        print(f"Endorsement creation failed: {endorsement_resp.text}")
        return
        
    endorsement = endorsement_resp.json()
    endorsement_id = endorsement['id']
    print(f"Endorsement draft created: {endorsement_id}")
    print_result("Endorsement Draft", endorsement)

    # 8. Approve Endorsement
    print("\n[8] Approving Endorsement...")
    approve_resp = session.post(f"{BASE_URL}/policies/endorsements/{endorsement_id}/approve")
    if approve_resp.status_code != 200:
        print(f"Endorsement approval failed: {approve_resp.text}")
        return
        
    updated_policy = approve_resp.json()
    print("Endorsement approved. Policy updated.")
    print_result("Updated Policy", updated_policy)
    
    # Verify premium increased
    if float(updated_policy['premium_amount']) == 275000: # 225000 + 50000
        print("SUCCESS: Premium amount updated correctly.")
    else:
        print(f"WARNING: Premium amount mismatch. Expected 275000, got {updated_policy['premium_amount']}")

    # 9. Cancel Policy
    print("\n[9] Canceling Policy...")
    cancel_data = {
        "cancellation_reason": "Testing cancellation flow",
        "effective_date": date.today().isoformat()
    }
    cancel_resp = session.post(f"{BASE_URL}/policies/{policy_id}/cancel", json=cancel_data)
    if cancel_resp.status_code != 200:
        print(f"Cancellation failed: {cancel_resp.text}")
        return
        
    canceled_policy = cancel_resp.json()
    print(f"Policy canceled. Status: {canceled_policy['status']}")

    # 10. Reinstate Policy
    print("\n[10] Reinstating Policy...")
    reinstate_resp = session.post(f"{BASE_URL}/policies/{policy_id}/reinstate")
    if reinstate_resp.status_code != 200:
        print(f"Reinstatement failed: {reinstate_resp.text}")
        return
        
    reinstated_policy = reinstate_resp.json()
    print(f"Policy reinstated. Status: {reinstated_policy['status']}")

if __name__ == "__main__":
    main()
