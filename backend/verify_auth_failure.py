import requests
import sys

BASE_URL = "http://localhost:8000/api/v1"

def test_auth_me_failure():
    print(f"Testing /auth/me with INVALID token at {BASE_URL}/auth/me ...")
    
    headers = {
        "Authorization": "Bearer invalid_token_string",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 401:
            print("SUCCESS: Received 401 Unauthorized as expected.")
        elif response.status_code == 500:
            print("FAILURE: Received 500 Internal Server Error.")
        else:
            print(f"Received unexpected status: {response.status_code}")
            
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    test_auth_me_failure()
