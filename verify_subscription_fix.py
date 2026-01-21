import requests
import sys

BASE_URL = "http://127.0.0.1:8000/api/v1"
LOGIN_URL = f"{BASE_URL}/auth/login"
SUBSCRIPTION_URL = f"{BASE_URL}/subscription/status"

# Using the account I just verified in v5 task
EMAIL = "johndoe_fix_confirmed_v5@example.com"
PASSWORD = "Password123!"

def verify_subscription():
    print(f"--- Starting Subscription Verification for {EMAIL} ---")
    
    # Login to get token
    print(f"Logging in as {EMAIL}...")
    try:
        resp = requests.post(LOGIN_URL, json={"email": EMAIL, "password": PASSWORD})
        if resp.status_code != 200:
            print(f"Login failed: {resp.status_code} {resp.text}")
            return False
        
        token = resp.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        
        # Call subscription status
        print(f"Calling GET {SUBSCRIPTION_URL}...")
        resp_sub = requests.get(SUBSCRIPTION_URL, headers=headers)
        
        if resp_sub.status_code == 200:
            data = resp_sub.json()
            print("SUCCESS: Subscription status retrieved!")
            print(f" - Plan: {data.get('plan')}")
            print(f" - Credits: {data.get('credits')}")
            print(f" - Company ID: {data.get('company_id')}")
            return True
        else:
            print(f"FAILURE: Subscription status returned {resp_sub.status_code}")
            print(f"Detail: {resp_sub.text}")
            return False

    except Exception as e:
        print(f"Verification Exception: {e}")
        return False

if __name__ == "__main__":
    success = verify_subscription()
    if success:
        print("SUBSCRIPTION VERIFICATION PASSED")
        sys.exit(0)
    else:
        print("SUBSCRIPTION VERIFICATION FAILED")
        sys.exit(1)
