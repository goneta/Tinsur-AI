import requests
import time
import uuid
import sys

BASE_URL = "http://127.0.0.1:8000/api/v1"
REGISTRATION_URL = f"{BASE_URL}/clients/"
LOGIN_URL = f"{BASE_URL}/auth/login"

EMAIL = f"johndoe_fix_confirmed_v5@example.com"
PASSWORD = "Password123!"

def verify():
    print(f"--- Starting Verification for {EMAIL} ---")
    
    # payload for self-registration (User + Client)
    payload = {
        "email": EMAIL,
        "password": PASSWORD,
        "first_name": "John",
        "last_name": "Doe",
        "phone": "+1234567890",
        "address": "123 Main St",
        "city": "New York",
        "country": "USA",
        "client_type": "individual",
        "driving_licence_number": "NY-12345678",
        "date_of_birth": "1990-01-01",
        "occupation": "Software Engineer",
        "preferred_language": "en"
    }

    print(f"Registering client at {REGISTRATION_URL}...")
    try:
        resp = requests.post(REGISTRATION_URL, json=payload)
        if resp.status_code == 400 and "already registered" in resp.text:
            print("Client already registered, proceeding to login and check.")
        elif resp.status_code != 201:
            print(f"Registration failed: {resp.status_code} {resp.text}")
            return False
        else:
            print("Registration successful!")
    except Exception as e:
        print(f"Registration Exception: {e}")
        return False

    # Login to get token and client info
    print(f"Logging in as {EMAIL}...")
    try:
        resp = requests.post(LOGIN_URL, json={"email": EMAIL, "password": PASSWORD})
        if resp.status_code != 200:
            print(f"Login failed: {resp.status_code} {resp.text}")
            return False
        
        data = resp.json()
        token = data.get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get current client info (includes drivers and automobile_details due to joinedload)
        print("Fetching client details (including drivers)...")
        resp_me = requests.get(f"{BASE_URL}/clients/me", headers=headers)
        if resp_me.status_code != 200:
            print(f"Failed to fetch client details: {resp_me.status_code} {resp_me.text}")
            return False
        
        client_info = resp_me.json()
        drivers = client_info.get("drivers", [])
        
        print(f"Found {len(drivers)} drivers for this client.")
        
        if len(drivers) > 0:
            main_driver = drivers[0]
            print(f"SUCCESS: Driver card found!")
            print(f" - Driver: {main_driver.get('first_name')} {main_driver.get('last_name')}")
            print(f" - License: {main_driver.get('license_number')}")
            return True
        else:
            print("FAILURE: No driver card was automatically generated.")
            return False

    except Exception as e:
        print(f"Verification Exception: {e}")
        return False

if __name__ == "__main__":
    success = verify()
    if success:
        print("VERIFICATION PASSED")
        sys.exit(0)
    else:
        print("VERIFICATION FAILED")
        sys.exit(1)
