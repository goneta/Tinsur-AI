import requests
import sys

BASE_URL = "http://127.0.0.1:8000/api/v1"
LOGIN_URL = "http://127.0.0.1:8000/api/v1/auth/login"
CLIENTS_URL = "http://127.0.0.1:8000/api/v1/clients/?limit=100"

EMAIL = "admin@demoinsurance.com"
PASSWORD = "admin123"

def test_clients():
    print(f"Logging in as {EMAIL}...")
    try:
        resp = requests.post(LOGIN_URL, json={"email": EMAIL, "password": PASSWORD})
        if resp.status_code != 200:
            print(f"Login failed: {resp.status_code} {resp.text}")
            return

        data = resp.json()
        token = data.get("access_token")
        if not token:
            print("No access token in response")
            return
            
        print(f"Login success. Token: {token[:10]}...")
        
        headers = {"Authorization": f"Bearer {token}"}
        print(f"Fetching clients from {CLIENTS_URL}...")
        
        # Explicitly handling the URL
        resp_clients = requests.get(CLIENTS_URL, headers=headers)
        
        if resp_clients.status_code == 200:
            clients = resp_clients.json()
            print(f"Success! Found {len(clients)} clients.")
            for c in clients:
                print(f" - {c.get('first_name')} {c.get('last_name')} ({c.get('email')})")
        else:
            print(f"Failed to fetch clients: {resp_clients.status_code}")
            print(resp_clients.text)

    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_clients()
