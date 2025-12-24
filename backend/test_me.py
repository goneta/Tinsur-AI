
import requests
import sys

def test_me():
    # first login to get token
    login_url = "http://localhost:8000/api/v1/auth/login"
    login_payload = {
        "email": "admin@demoinsurance.com",
        "password": "Admin123!"
    }
    
    print("Logging in...")
    try:
        session = requests.Session()
        r = session.post(login_url, json=login_payload)
        if r.status_code != 200:
            print(f"Login failed: {r.text}")
            return
            
        token = r.json()['access_token']
        print("Login success. Testing /auth/me...")
        
        headers = {"Authorization": f"Bearer {token}"}
        r = session.get("http://localhost:8000/api/v1/auth/me", headers=headers, timeout=5)
        print(f"Me Status: {r.status_code}")
        print(f"Me Response: {r.text}")
        
    except Exception as e:
        print(f"Request Failed: {e}")

if __name__ == "__main__":
    test_me()
