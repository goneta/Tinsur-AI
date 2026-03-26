
import requests
import sys

def test_login():
    url = "http://localhost:8000/api/v1/auth/login"
    payload = {
        "email": "admin@demoinsurance.com",
        "password": "Admin123!"
    }
    
    print(f"Attempting login to {url} with {payload['email']}...")
    try:
        response = requests.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("LOGIN SUCCESS!")
        else:
            print("LOGIN FAILED.")
    except Exception as e:
        print(f"Request Error: {e}")

if __name__ == "__main__":
    test_login()
