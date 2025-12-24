import requests
import os

API_URL = "http://localhost:8002/api/v1"
EMAIL = "admin@demoinsurance.com"
PASSWORD = "Admin123!"

def test_upload():
    print(f"Logging in as {EMAIL}...")
    try:
        # 1. Login
        # Try JSON with email
        resp = requests.post(f"{API_URL}/auth/login", json={"email": EMAIL, "password": PASSWORD})
        if resp.status_code != 200:
             # Try username
             resp = requests.post(f"{API_URL}/auth/login", json={"username": EMAIL, "password": PASSWORD})
        
        if resp.status_code != 200:
            print(f"Login failed: {resp.status_code} {resp.text}")
            return
            
        token = resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("Login success. Token received.")
        
        # 2. Upload File
        print("Uploading dummy.pdf...")
        # Create dummy file
        with open("dummy.pdf", "wb") as f:
            f.write(b"dummy content")
            
        files = {"file": ("dummy.pdf", open("dummy.pdf", "rb"), "application/pdf")}
        data = {"label": "Document"}
        
        upload_resp = requests.post(f"{API_URL}/documents/upload", headers=headers, files=files, data=data)
        
        print(f"Upload Response: {upload_resp.status_code}")
        print(f"Body: {upload_resp.text}")
        
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_upload()
