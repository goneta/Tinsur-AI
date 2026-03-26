import requests
import sys

BASE_URL = "http://127.0.0.1:8000/api/v1"

def test_list_fallback():
    print("Testing GET /quotes with INVALID Token (expecting Fallback)...")
    
    # Use a JUNK token to force 401/None user in backend
    # This triggers the 'else' block in list_quotes
    headers = {"Authorization": "Bearer iamastaletoken_for_list_test"}
    
    url = f"{BASE_URL}/quotes/"
    try:
        # TEST 1: Authenticated (Basline)
        print("\nTEST 1: Authenticated Fetch (Baseline)...")
        # Reuse login from verify_full_flow logic or just hardcode new login here? 
        # Better to incorporate login function.
        login_resp = requests.post(f"{BASE_URL}/auth/login", json={"email": "admin@demoinsurance.com", "password": "Password123!"})
        if login_resp.status_code == 200:
             valid_token = login_resp.json()["access_token"]
             headers_valid = {"Authorization": f"Bearer {valid_token}"}
             resp_valid = requests.get(url, headers=headers_valid)
             print(f"   Auth Response Status: {resp_valid.status_code}")
        else:
             print("   Skipping Auth Test (Login Failed)")

        # TEST 2: Fallback (Invalid Token)
        print("\nTEST 2: Fallback Fetch (Invalid Token)...")
        response = requests.get(url, headers=headers)
        
        print(f"   Fallback Response Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            # print(f"Response: {data}")
            quotes = data.get("quotes", [])
            print(f"SUCCESS. Quotes found: {len(quotes)}")
            if len(quotes) > 0:
                print(f"First Quote ID: {quotes[0].get('id')}")
        else:
            print(f"FAILURE. Response: {response.text}")
            
    except Exception as e:
        print(f"EXCEPTION: {e}")

if __name__ == "__main__":
    test_list_fallback()
