
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
        # Try registering
        return register()

def register():
    print(f"Registering {CLIENT_EMAIL}...")
    try:
        suffix = CLIENT_EMAIL.split('_')[1].split('@')[0]
        response = requests.post(f"{BASE_URL}/auth/register", json={
            "email": CLIENT_EMAIL,
            "password": CLIENT_PASSWORD,
            "first_name": "Test",
            "last_name": "Client",
            "company_name": f"TestCorp_{suffix}",
            "company_subdomain": f"testcorp_{suffix}"
        })
        response.raise_for_status()
        print("Registration successful.")
        return login()
    except Exception as e:
        print(f"Registration failed: {e}")
        if hasattr(e, 'response') and e.response is not None:
             print(f"Response: {e.response.text}")
        return None

        return None

def chat(token, message, history=[]):
    print(f"\nUser: {message}")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Prepare history payload
    history_payload = [{"role": h["role"], "content": h["content"]} for h in history]
    
    try:
        response = requests.post(f"{BASE_URL}/chat/", json={
            "message": message,
            "history": history_payload
        }, headers=headers)
        response.raise_for_status()
        data = response.json()
        print(f"Agent: {data['response']}")
        return data['response']
    except Exception as e:
        print(f"Chat failed: {e}")
        return None

def main():
    print("Starting Sales Agent Verification...")
    # Use a unique email to avoid stale state/claims
    global CLIENT_EMAIL 
    CLIENT_EMAIL = f"client_{os.urandom(4).hex()}@example.com"
    
    token = register() # Always register new
    if not token:
        print("Register failed, trying login (fallback)")
        token = login()
        
    if not token:
        sys.exit(1)
        
    history = []
    
    # 1. Trigger Quote Flow
    msg1 = "I want to get a new insurance quote."
    resp1 = chat(token, msg1, history)
    if resp1:
        history.append({"role": "user", "content": msg1})
        history.append({"role": "assistant", "content": resp1})
    
    # 2. Provide Details
    if "eligible" in str(resp1).lower() or "policies" in str(resp1).lower():
        print("SUCCESS: Agent found eligible policies immediately.")
    else:
        # Agent likely asked for details or acknowledge
        msg2 = "I am 35 years old. I have had my license for 10 years and 0 accidents."
        resp2 = chat(token, msg2, history)
        if resp2:
            history.append({"role": "user", "content": msg2})
            history.append({"role": "assistant", "content": resp2})
            
            if "policy" in str(resp2).lower() or "plan" in str(resp2).lower():
                 print("SUCCESS: Agent proceeded to policy selection.")
            else:
                 print("DEBUG: Logic needs check. Agent response might be ambiguous.")

    # 3. Select Policy
    msg3 = "I choose the Gold plan."
    resp3 = chat(token, msg3, history)
    if resp3:
        history.append({"role": "user", "content": msg3})
        history.append({"role": "assistant", "content": resp3})
    
    # 4. Check results
    last_resp = history[-1]["content"] if history else ""
    if "quote" in last_resp.lower() or "Reference" in last_resp:
        print("SUCCESS: Quote generated.")

if __name__ == "__main__":
    main()
