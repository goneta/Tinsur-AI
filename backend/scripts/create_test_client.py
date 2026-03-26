
import requests
import json
import sys

BASE_URL = "http://localhost:8000/api/v1"
EMAIL = "test_client@tinsur.ai"
PASSWORD = "Password123!"

def login():
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json={
            "email": EMAIL,
            "password": PASSWORD
        })
        if response.status_code == 200:
            print("User already exists and login successful.")
            return True
    except:
        pass
    return False

def register():
    print(f"Creating user {EMAIL}...")
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json={
            "email": EMAIL,
            "password": PASSWORD,
            "first_name": "Test",
            "last_name": "User",
            "company_name": "TestCompany_User",
            "company_subdomain": "test_user_subdomain"
        })
        if response.status_code == 200 or response.status_code == 201:
            print("Registration successful!")
            return True
        else:
            print(f"Registration failed: {response.text}")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    if not login():
        register()
    
    print("\n" + "="*50)
    print("✅ TEST LOGIN DETAILS")
    print("="*50)
    print(f"URL:      http://localhost:3000/portal/login")
    print(f"Email:    {EMAIL}")
    print(f"Password: {PASSWORD}")
    print("="*50 + "\n")
