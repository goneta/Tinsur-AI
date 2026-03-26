import sys
import os
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"
LOGIN_URL = f"{BASE_URL}/auth/login"

def verify_login():
    print(f"Attempting login to {LOGIN_URL}...")
    payload = {
        "email": "admin@demoinsurance.com",
        "password": "admin"
    }
    
    try:
        response = requests.post(LOGIN_URL, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            user = data.get("user", {})
            print("Login SUCCESS!")
            print(f"User ID: {user.get('id')}")
            print(f"Email: {user.get('email')}")
            print(f"Role: {user.get('role')}")
            
            if user.get("role") == "company_admin":
                print("Role Verification: PASS")
            else:
                print(f"Role Verification: FAIL (Expected 'company_admin', got '{user.get('role')}')")
                
        else:
            print(f"Login FAILED! Status: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"Exception during login verification: {e}")

if __name__ == "__main__":
    verify_login()
