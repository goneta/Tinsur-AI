import requests
import json
import random
import string
from datetime import datetime, timedelta

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

def get_policy_type(headers):
    print_step("Getting Policy Type")
    response = requests.get(f"{BASE_URL}/policy-types/", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        types = data.get("policy_types", [])
        if types:
            print_result(f"Found {len(types)} policy types")
            # Prefer 'Automobile' or similar if available, else pick first
            for pt in types:
                if 'auto' in pt['name'].lower() or 'vehicle' in pt['name'].lower():
                    return pt
            return types[0]
        else:
            print_result("No policy types found", False)
            exit(1)
    else:
        print_result(f"Failed to get policy types: {response.text}", False)
        exit(1)

def get_current_user(headers):
    print_step("Getting User Info")
    response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print_result(f"Failed to get user info: {response.text}", False)
        exit(1)

def create_client(headers, company_id):
    print_step("Creating Client")
    random_str = ''.join(random.choices(string.ascii_lowercase, k=5))
    client_data = {
        "company_id": company_id,
        "first_name": "Test",
        "last_name": f"Client_{random_str}",
        "email": f"test.client.{random_str}@example.com",
        "phone": "+22501020304",
        "client_type": "individual",
        "address": "123 Test St, Abidjan"
    }
    
    response = requests.post(f"{BASE_URL}/clients/", headers=headers, json=client_data)
    
    if response.status_code == 201:
        client = response.json()
        print_result(f"Client created: {client['first_name']} {client['last_name']}")
        return client
    else:
        print_result(f"Failed to create client: {response.text}", False)
        exit(1)

def calculate_quote(headers, client_id, policy_type_id):
    print_step("Calculating Quote Premium")
    calc_data = {
        "client_id": client_id,
        "policy_type_id": policy_type_id,
        "coverage_amount": 5000000,
        "duration_months": 12,
        "premium_frequency": "annual",
        "risk_factors": {
            "vehicle_value": 5000000,
            "vehicle_age": 2
        }
    }
    
    response = requests.post(f"{BASE_URL}/quotes/calculate", headers=headers, json=calc_data)
    
    if response.status_code == 200:
        result = response.json()
        print_result(f"Calculation successful. Final Premium: {result['final_premium']}")
        return result
    else:
        print_result(f"Quote calculation failed: {response.text}", False)
        return None

def create_quote(headers, client_id, policy_type_id):
    print_step("Creating Quote")
    quote_data = {
        "client_id": client_id,
        "policy_type_id": policy_type_id,
        "coverage_amount": 5000000,
        "duration_months": 12,
        "premium_frequency": "annual",
        "details": {
            "vehicle_brand": "Toyota",
            "vehicle_model": "Corolla",
            "registration_number": "AB-123-CD"
        }
    }
    
    response = requests.post(f"{BASE_URL}/quotes/", headers=headers, json=quote_data)
    
    if response.status_code == 201:
        quote = response.json()
        print_result(f"Quote created: {quote['quote_number']}")
        return quote
    else:
        print_result(f"Failed to create quote: {response.text}", False)
        exit(1)

def send_quote(headers, quote_id):
    print_step("Sending Quote")
    response = requests.post(f"{BASE_URL}/quotes/{quote_id}/send", headers=headers)
    
    if response.status_code == 200:
        quote = response.json()
        if quote['status'] == 'sent':
            print_result("Quote marked as sent")
            return quote
        else:
            print_result(f"Quote status mismatch: {quote['status']}", False)
            exit(1)
    else:
        print_result(f"Failed to send quote: {response.text}", False)
        exit(1)

def convert_quote(headers, quote_id):
    print_step("Converting Quote to Policy")
    conversion_data = {
        "start_date": datetime.now().strftime("%Y-%m-%d"),
        "payment_method": "cash",
        "initial_payment_amount": 150000
    }
    
    response = requests.post(f"{BASE_URL}/quotes/{quote_id}/convert", headers=headers, json=conversion_data)
    
    if response.status_code == 201:
        result = response.json()
        print_result(f"Conversion successful. Policy Number: {result['policy_number']}")
        return result
    else:
        print_result(f"Failed to convert quote: {response.text}", False)
        exit(1)

def main():
    print("Starting Quote Flow Verification...")
    
    try:
        token = get_auth_token()
        headers = {"Authorization": f"Bearer {token}"}
        
        user = get_current_user(headers)
        company_id = user['company_id']
        
        policy_type = get_policy_type(headers)
        client = create_client(headers, company_id)
        
        # Test Calculation
        calculate_quote(headers, client['id'], policy_type['id'])
        
        # Create Quote
        quote = create_quote(headers, client['id'], policy_type['id'])
        
        # Send Quote
        send_quote(headers, quote['id'])
        
        # Convert to Policy
        convert_quote(headers, quote['id'])
        
        print("\n✅ All Quote Flow tests passed successfully!")
        
    except Exception as e:
        print_result(f"An unexpected error occurred: {str(e)}", False)

if __name__ == "__main__":
    main()
