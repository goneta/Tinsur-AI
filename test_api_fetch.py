import requests
import json

BASE_URL = "http://localhost:8000/api/v1"
EMAIL = "admin@demoinsurance.com"
PASSWORD = "Admin123!"

def test_api():
    print(f"Logging in as {EMAIL}...")
    try:
        login_res = requests.post(f"{BASE_URL}/auth/login", json={
            "email": EMAIL,
            "password": PASSWORD
        })
        if login_res.status_code != 200:
            print(f"Login failed: {login_res.status_code} - {login_res.text}")
            return
            
        token = login_res.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        
        print("\nChecking /auth/me...")
        me = me_res.json()
        print(f"Me: {me['email']} (Company: {me['company_id']}, Role: {me['role']})")
        
        print("\nFetching /clients...")
        clients_res = requests.get(f"{BASE_URL}/clients", headers=headers)
        print(f"Status: {clients_res.status_code}")
        if clients_res.status_code == 200:
            clients = clients_res.json()
            print(f"Found {len(clients)} clients.")
            for c in clients[:5]:
                print(f"- {c['first_name']} {c['last_name']} (Company: {c['company_id']})")
        else:
            print(f"Failed to fetch clients: {clients_res.text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_api()
