import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_login_api():
    url = f"{BASE_URL}/auth/login"
    payload = {
        "email": "admin@demoinsurance.com",
        "password": "Password123!"
    }
    headers = {
        "Content-Type": "application/json"
    }
    
    print(f"POST {url} with {payload['email']}...")
    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"Status Code: {response.status_code}")
        print("Response Body:")
        print(response.text)
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_login_api()
