import requests
import sys

BASE_URL = "http://localhost:8000/api/v1"

def verify_api():
    # 1. Login
    try:
        login_resp = requests.post("http://localhost:8000/api/v1/login/access-token", data={
            "username": "admin@demoinsurance.com",
            "password": "password123"
        })
        if login_resp.status_code != 200:
            print(f"Login Failed: {login_resp.text}")
            return
        
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("Login Successful.")
        
        # 2. Get Clients
        print("\nFetching Clients...")
        clients_resp = requests.get(f"{BASE_URL}/clients/?limit=100", headers=headers)
        if clients_resp.status_code == 200:
            clients = clients_resp.json()
            print(f"Clients Found: {len(clients)}")
            for c in clients:
                print(f" - {c.get('first_name')} {c.get('last_name')} ({c.get('email')})")
        else:
            print(f"Get Clients Failed: {clients_resp.text}")

        # 3. Get Premium Policies
        print("\nFetching Policies...")
        # Assuming endpoint is /premium-policies/ or similar. Let's guess or check task. 
        # Actually usually it's /policies/premium or similar.
        pol_resp = requests.get(f"{BASE_URL}/premium-policies/", headers=headers)
        if pol_resp.status_code == 200:
            pols = pol_resp.json()
            print(f"Policies Found: {len(pols)}")
            for p in pols:
                print(f" - {p.get('name')}")
        else:
            print(f"Get Policies Failed: {pol_resp.status_code} (Endpoint might be different)")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    verify_api()
