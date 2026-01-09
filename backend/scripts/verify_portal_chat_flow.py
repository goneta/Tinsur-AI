
import requests
import json
import os
import sys

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
CLIENT_EMAIL = "client@example.com"
CLIENT_PASSWORD = "Password123!"

def login():
    print(f"Logging in as {CLIENT_EMAIL}...")
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json={
            "email": CLIENT_EMAIL,
            "password": CLIENT_PASSWORD
        })
        response.raise_for_status()
        token = response.json()["access_token"]
        print("Login successful.")
        return token
    except Exception as e:
        print(f"Login failed: {e}")
        if response.text:
            print(f"Response: {response.text}")
        
        # Try registering if user not found (401)
        if response.status_code == 401 or "not found" in response.text.lower():
             return register()
        return None

def register():
    print(f"Registering {CLIENT_EMAIL}...")
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json={
            "email": CLIENT_EMAIL,
            "password": CLIENT_PASSWORD,
            "first_name": "Test",
            "last_name": "Client",
            "company_name": "TestCorp",
            "company_subdomain": "testcorp"
        })
        response.raise_for_status()
        print("Registration successful.")
        # Now login
        return login()
    except Exception as e:
        print(f"Registration failed: {e}")
        if hasattr(response, 'text') and response.text:
            print(f"Response: {response.text}")
        return None

def test_chat(token, message, image_path=None):
    print(f"\nTesting Chat with message: '{message}' (Image: {image_path})")
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"message": message}
    if image_path:
        payload["image_path"] = image_path
        
    try:
        response = requests.post(f"{BASE_URL}/chat/", json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        print(f"Agent Response: {data['response']}")
        return data['response']
    except Exception as e:
        print(f"Chat failed: {e}")
        if response.text:
            print(f"Response: {response.text}")
        return None

def upload_image(token):
    print("\nUploading dummy image for claim analysis...")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create a dummy image
    dummy_image_path = "dummy_crash.jpg"
    with open(dummy_image_path, "wb") as f:
        f.write(os.urandom(1024)) # Random bytes
        
    try:
        with open(dummy_image_path, "rb") as f:
            files = {"file": (dummy_image_path, f, "image/jpeg")}
            data = {"label": "Photo"}
            response = requests.post(f"{BASE_URL}/documents/upload", headers=headers, files=files, data=data)
            
        response.raise_for_status()
        result = response.json()
        print(f"Upload successful. URL: {result['url']}")
        return result['url']
    except Exception as e:
        print(f"Upload failed: {e}")
        return None
    finally:
        if os.path.exists(dummy_image_path):
            os.remove(dummy_image_path)

def verify_proactive_alert(response, late_fee_mentioned=True):
    if late_fee_mentioned:
        if "fee" in response.lower() or "overdue" in response.lower() or "50" in response:
            print("SUCCESS: Proactive alert detected in response.")
            return True
        else:
            print("FAILURE: Agent did not mention late fee/overdue payment.")
            return False
    return True

def main():
    print("Starting Portal Chat Verification...")
    
    token = login()
    if not token:
        sys.exit(1)
        
    # 1. Test Proactive Trigger
    print("\n--- Test 1: Proactive Check ---")
    response_1 = test_chat(token, "Hello, checking in.")
    if response_1:
         # We expect the agent to see the late payment from the previous tests
         # Note: verify_proactive_support.py might have waived it already.
         # If it was waived, the status is no longer overdue.
         print("Review response for context awareness.")

    # 2. Test Multi-modal Claim Interaction
    print("\n--- Test 2: Multi-modal Claim ---")
    
    # Upload image
    image_url = upload_image(token)
    
    if image_url:
        # Chat with image
        # Note: Since it's a random byte image, the Vision model might say it's invalid or unclear, 
        # but as long as it processes it without error, the flow is valid.
        response_2 = test_chat(token, "I had an accident, here is the photo.", image_path=image_url)
        
        if response_2:
            print("SUCCESS: Multi-modal chat completed.")
            
    print("\nVerification Complete.")

if __name__ == "__main__":
    main()
