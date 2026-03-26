
import requests
import json
import random
import string
from uuid import uuid4

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
EMAIL = "admin@demoinsurance.com"
PASSWORD = "Admin123!"

def print_step(message):
    print(f"\n{'='*50}")
    print(f"STEP: {message}")
    print(f"{'='*50}")

def print_result(message, success=True):
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status}: {message}")

def get_auth_token():
    print_step("Authenticating")
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": EMAIL,
        "password": PASSWORD
    })
    
    if response.status_code == 200:
        print_result("Login successful")
        return response.json()["access_token"]
    else:
        print_result(f"Login failed: {response.text}", False)
        exit(1)

def create_criteria(headers, field, operator, value):
    print_step(f"Creating Criteria: {field} {operator} {value}")
    data = {
        "name": f"Test Criteria {field}",
        "field_name": field,
        "operator": operator,
        "value": value
    }
    response = requests.post(f"{BASE_URL}/premium-policies/criteria", headers=headers, json=data)
    if response.status_code == 201:
        print_result("Criteria created")
        return response.json()['id']
    else:
        print_result(f"Failed to create criteria: {response.text}", False)
        exit(1)

def create_policy_type(headers, name, criteria_ids):
    print_step(f"Creating Policy Type: {name}")
    data = {
        "name": name,
        "price": 100.00,
        "criteria_ids": criteria_ids
    }
    response = requests.post(f"{BASE_URL}/premium-policies/types", headers=headers, json=data)
    if response.status_code == 201:
        print_result("Policy Type created")
        return response.json()['id']
    else:
        print_result(f"Failed to create policy type: {response.text}", False)
        exit(1)

def test_eligibility(headers, policy_type_id, description, vehicle_details, driver_details, should_match):
    print_step(f"Testing Match: {description}")
    
    payload = {
        # No client_id, purely ephemeral
        "vehicle_details": vehicle_details,
        "driver_details": driver_details
    }
    
    response = requests.post(f"{BASE_URL}/premium-policies/match", headers=headers, json=payload)
    
    if response.status_code == 200:
        data = response.json()
        matched_policies = data.get('data', [])
        matched_ids = [p['id'] for p in matched_policies]
        
        is_matched = policy_type_id in matched_ids
        
        if is_matched == should_match:
            print_result(f"Match result as expected: {is_matched}")
        else:
            print_result(f"Unexpected match result. Expected {should_match}, got {is_matched}. Matched: {matched_ids}", False)
    elif response.status_code == 404 and not should_match: 
             # 404 might be returned if no policies match at all
             print_result("Match result as expected (No policies found)")
    else:
        print_result(f"API Error: {response.status_code} {response.text}", False)

def main():
    print("Starting Eligibility Logic Verification...")
    try:
        token = get_auth_token()
        headers = {"Authorization": f"Bearer {token}"}
        
        # 1. Setup Data
        # Criteria: Age > 25 AND License Years >= 3
        crit_age_id = create_criteria(headers, "age", ">", "25")
        crit_license_id = create_criteria(headers, "driving_license_years", ">=", "3")
        
        policy_id = create_policy_type(headers, "Mature Driver Gold", [crit_age_id, crit_license_id])
        
        # 2. Test Cases
        
        # Case A: Eligible (Age 30, License 5)
        test_eligibility(
            headers, policy_id, "Eligible Driver (30yo, 5y license)",
            vehicle_details={"value": 10000},
            driver_details={"age": 30, "license_years": 5},
            should_match=True
        )
        
        # Case B: Ineligible (Age 20, License 5)
        test_eligibility(
            headers, policy_id, "Ineligible Driver (20yo, 5y license)",
            vehicle_details={"value": 10000},
            driver_details={"age": 20, "license_years": 5},
            should_match=False
        )

        # Case C: Ineligible (Age 30, License 1)
        test_eligibility(
            headers, policy_id, "Ineligible Driver (30yo, 1y license)",
            vehicle_details={"value": 10000},
            driver_details={"age": 30, "license_years": 1},
            should_match=False
        )
        
        print("\n✅ Verification Complete")
        
    except Exception as e:
        print_result(f"An unexpected error occurred: {str(e)}", False)

if __name__ == "__main__":
    main()
