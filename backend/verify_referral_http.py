import requests
import sys

BASE_URL = "http://localhost:8000/api/v1"
EMAIL = "test_client@tinsur.ai"
PASSWORD = "password123"

def verify_http():
    try:
        # 1. Login
        print(f"Logging in as {EMAIL}...")
        # Note: Using /auth/login based on code inspection
        resp = requests.post(f"{BASE_URL}/auth/login", json={
            "email": EMAIL, 
            "password": PASSWORD
        })
        
        if resp.status_code != 200:
            print(f"Login Failed: {resp.status_code} - {resp.text}")
            return
        
        data = resp.json()
        token = data.get("access_token")
        if not token:
            print(f"Login success but no token? Keys: {data.keys()}")
            return
            
        print("Login success. Token obtained.")
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # 2. Test Referral Generation
        print("Attempting to generate referral code...")
        ref_resp = requests.post(f"{BASE_URL}/portal/referrals", headers=headers)
        
        print(f"Referral Response Code: {ref_resp.status_code}")
        print(f"Referral Response Body: {ref_resp.text}")
        
        if ref_resp.status_code == 200:
            data = ref_resp.json()
            print("\nSUCCESS!")
            print(f"Referral Code: {data.get('referral_code')}")
            print(f"Status: {data.get('status')}")
        else:
            print("\nFAILURE!")
            
    except Exception as e:
        print(f"Uncaught Error: {e}")

if __name__ == "__main__":
    verify_http()
