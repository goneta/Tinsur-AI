import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_auth():
    print("--- Testing Auth Behavior for /clients ---")

    # 1. Test without token (Should be 200 OK, empty list if unauth allowed)
    try:
        res = requests.get(f"{BASE_URL}/clients/")
        print(f"No Token: Code={res.status_code}")
    except Exception as e:
        print(f"No Token: Failed {e}")

    # 2. Test with INVALID token (Should be 200 OK if get_optional_user works as intended, or 401 if strict)
    try:
        headers = {"Authorization": "Bearer invalid_token_string"}
        res = requests.get(f"{BASE_URL}/clients/", headers=headers)
        print(f"Invalid Token: Code={res.status_code}")
        if res.status_code != 200:
             print(f"Response: {res.text}")
    except Exception as e:
        print(f"Invalid Token: Failed {e}")

    # 3. Login to get valid token
    token = None
    try:
        # Assuming there is a user admin@demoinsurance.com / Password123!
        auth_data = {
            "username": "admin@demoinsurance.com",
            "password": "Password123!"
        }
        res = requests.post(f"{BASE_URL}/auth/login", data=auth_data)
        if res.status_code == 200:
            token = res.json()["access_token"]
            print(f"Login: Success")
        else:
            print(f"Login: Failed {res.status_code} {res.text}")
    except Exception as e:
        print(f"Login Error: {e}")

    if token:
        # 4. Test with VALID token
        try:
            headers = {"Authorization": f"Bearer {token}"}
            res = requests.get(f"{BASE_URL}/clients/", headers=headers)
            print(f"Valid Token: Code={res.status_code}")
        except Exception as e:
            print(f"Valid Token: Failed {e}")

if __name__ == "__main__":
    test_auth()
