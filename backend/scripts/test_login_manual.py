import requests
import sys

def test_login():
    url = "http://localhost:8000/api/v1/auth/login"
    data = {
        "email": "admin@demoinsurance.com",
        "password": "admin123"
    }
    try:
        print(f"Testing login at {url}...")
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("Login SUCCESS!")
        else:
            print("Login FAILED!")
            
    except Exception as e:
        print(f"Connection Error: {e}")

if __name__ == "__main__":
    test_login()
