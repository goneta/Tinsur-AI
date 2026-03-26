
import requests
import sys

BASE_URL = "http://localhost:8000/api/v1"
LOGIN_DATA = {
    "email": "admin@demoinsurance.com",
    "password": "Password123!"
}

def verify_client_fetch():
    print("--- Step 1: Login ---")
    response = requests.post(f"{BASE_URL}/auth/login", json=LOGIN_DATA)
    if response.status_code != 200:
        print(f"Login failed: {response.status_code} - {response.text}")
        sys.exit(1)

    tokens = response.json()
    access_token = tokens["access_token"]
    print(f"Login successful. Got token.")

    print("\n--- Step 2: Fetch Clients (Exact Frontend Call) ---")
    # Frontend calls: /clients with limit=1000 and _t timestamp
    # AND it was calling /clients/ originally. I changed it to /clients.
    # Let's test BOTH to see the behavior.
    
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"limit": 1000, "_t": "123456789"}

    # Test 1: No Trailing Slash (Current Code)
    url_no_slash = f"{BASE_URL}/clients"
    print(f"Requesting: GET {url_no_slash}")
    res1 = requests.get(url_no_slash, headers=headers, params=params)
    print(f"Result (No Slash): {res1.status_code}")
    if res1.status_code != 200:
        print(f"Error Body: {res1.text}")

    # Test 2: Trailing Slash (Old Code)
    url_slash = f"{BASE_URL}/clients/"
    print(f"\nRequesting: GET {url_slash}")
    res2 = requests.get(url_slash, headers=headers, params=params)
    print(f"Result (Slash): {res2.status_code}")
    if res2.status_code != 200:
        print(f"Error Body: {res2.text}")
        
    print("\n--- Step 3: Check /auth/me to confirm token validity ---")
    res_me = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    print(f"Token Valid? {res_me.status_code}")

if __name__ == "__main__":
    verify_client_fetch()
