import requests
import sys

def verify_login():
    url = "http://localhost:8000/api/v1/auth/login"
    # Credentials set by create_admin_standalone.py
    payload = {
        "email": "admin@demoinsurance.com",
        "password": "admin123" 
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
    verify_login()
