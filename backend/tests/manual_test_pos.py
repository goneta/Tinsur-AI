import requests
import json
from datetime import datetime
import os
import sys

# Add backend directory to python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
ADMIN_EMAIL = "admin@example.com"  # Replace with valid admin email if different
ADMIN_PASSWORD = "password" # Replace with valid admin password if different

def login():
    print("Logging in...")
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": ADMIN_EMAIL, 
        "password": ADMIN_PASSWORD
    })
    if response.status_code == 200:
        token = response.json().get("access_token")
        print("Login successful.")
        return token
    else:
        print(f"Login failed: {response.text}")
        return None

def test_pos_flow(token):
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Create POS Location
    print("\n1. Creating POS Location...")
    pos_data = {
        "name": "Downtown Branch",
        "city": "Abidjan",
        "region": "Lagunes",
        "address": "123 Main St"
    }
    res = requests.post(f"{BASE_URL}/pos/locations", json=pos_data, headers=headers)
    if res.status_code == 200:
        pos_location = res.json()
        print(f"POS Location created: {pos_location['id']}")
    else:
        print(f"Failed to create POS: {res.text}")
        return

    # 2. Add Inventory
    print("\n2. Adding Inventory...")
    inv_data = {
        "pos_location_id": pos_location['id'],
        "item_name": "Brochures",
        "quantity": 500
    }
    res = requests.post(f"{BASE_URL}/pos/inventory", json=inv_data, headers=headers)
    if res.status_code == 200:
        print("Inventory added.")
    else:
        print(f"Failed to add inventory: {res.text}")

    # 3. Verify Sales Reports (Empty initially or existing data)
    print("\n3. Checking Sales Summary...")
    res = requests.get(f"{BASE_URL}/sales-reports/summary", headers=headers)
    if res.status_code == 200:
        print(f"Sales Summary: {res.json()}")
    else:
        print(f"Failed to get summary: {res.text}")

    print("\n4. Checking Sales by Channel...")
    res = requests.get(f"{BASE_URL}/sales-reports/by-channel", headers=headers)
    if res.status_code == 200:
        print(f"Sales by Channel: {res.json()}")
    else:
        print(f"Failed to get channel stats: {res.text}")

    print("\nTest completed.")

if __name__ == "__main__":
    token = login()
    if token:
        test_pos_flow(token)
