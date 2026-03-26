import requests
import sys

BASE_URL = "http://localhost:8000/api/v1"

def verify_api():
    print("1. Attempting Login...")
    try:
        # ENDPOINT CHANGED: /auth/login with JSON
        login_resp = requests.post(f"{BASE_URL}/auth/login", json={
            "email": "admin@demoinsurance.com",
            "password": "password123"
        })
        
        if login_resp.status_code != 200:
            print(f"Login Failed: {login_resp.status_code} {login_resp.text}")
            return
        
        data = login_resp.json()
        token = data.get("access_token")
        if not token:
             # Check if it returns just 'access_token' or nested
             print(f"Login Response keys: {data.keys()}")
             return

        headers = {"Authorization": f"Bearer {token}"}
        print("Login Successful.")
        
        # 2. Get User Info (verify company)
        me_resp = requests.get(f"{BASE_URL}/users/me", headers=headers)
        if me_resp.status_code == 200:
            user = me_resp.json()
            print(f"Logged in as: {user['email']}")
            print(f"Company ID: {user['company_id']}")
        else:
             # Try /auth/me if users/me doesn't exist
             me_resp = requests.get(f"{BASE_URL}/auth/me", headers=headers)
             if me_resp.status_code == 200:
                 user = me_resp.json()
                 print(f"Logged in as: {user['email']}")
                 print(f"Company ID: {user['company_id']}")
             else:
                 print(f"Get Me Failed: {me_resp.status_code}")
        
        # 3. Get Clients
        print("\nFetching Clients...")
        clients_resp = requests.get(f"{BASE_URL}/clients/?limit=100", headers=headers)
        if clients_resp.status_code == 200:
            clients = clients_resp.json()
            print(f"Clients Found: {len(clients)}")
            for c in clients:
                print(f" - {c.get('first_name')} {c.get('last_name')} ({c.get('email')})")
        else:
            print(f"Get Clients Failed: {clients_resp.text}")

        # 4. Get Premium Policies
        print("\nFetching Policies...")
        # Try both likely endpoints
        pol_resp = requests.get(f"{BASE_URL}/premium-policies/", headers=headers)
        if pol_resp.status_code == 200:
            pols = pol_resp.json()
            print(f"Policies Found: {len(pols)}")
            for p in pols:
                print(f" - {p.get('name')}")
        else:
             # Try policies/premium
             pol_resp = requests.get(f"{BASE_URL}/policies/premium", headers=headers)
             if pol_resp.status_code == 200:
                 pols = pol_resp.json()
                 print(f"Policies Found (alt path): {len(pols)}")
             else:
                 print(f"Get Policies Failed: {pol_resp.status_code}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    verify_api()
