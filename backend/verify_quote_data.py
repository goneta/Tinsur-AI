
import requests
import json
import sqlite3

BASE_URL = "http://localhost:8000/api/v1"
DB_PATH = "./insurance.db"

def check_latest_quote():
    # 1. Login
    print("Logging in...")
    login_resp = requests.post(f"{BASE_URL}/auth/login", json={"email": "admin@demoinsurance.com", "password": "Password123!"})
    if login_resp.status_code != 200:
        print("Login failed")
        return
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Get Quotes
    print("Fetching Quotes...")
    resp = requests.get(f"{BASE_URL}/quotes/", headers=headers, params={"limit": 1})
    if resp.status_code != 200:
        print(f"Failed to fetch quotes: {resp.text}")
        return
    
    data = resp.json()
    quotes = data if isinstance(data, list) else data.get("quotes", [])
    
    if not quotes:
        print("No quotes found.")
        return

    latest_quote = quotes[0]
    print(f"Latest Quote ID: {latest_quote['id']}")
    print(f"Policy Type ID: {latest_quote['policy_type_id']}")
    print(f"Included Services (in Quote Snapshot): {latest_quote.get('included_services')}")

    # 3. Check Policy Type in DB directly to see if source data exists
    policy_type_id = latest_quote['policy_type_id']
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print(f"\nChecking Source Policy Type {policy_type_id}...")
    cursor.execute("SELECT name, price FROM premium_policy_types WHERE id = ?", (policy_type_id,))
    pt = cursor.fetchone()
    if pt:
        print(f"Policy Type Found: {pt}")
    else:
        print("Policy Type NOT FOUND in DB!")
        return

    # Check Linked Services
    print("Checking linked services...")
    cursor.execute("""
        SELECT ps.name_en 
        FROM policy_services ps
        JOIN premium_policy_service_association ppsa ON ps.id = ppsa.service_id
        WHERE ppsa.policy_type_id = ?
    """, (policy_type_id,))
    
    services = cursor.fetchall()
    print(f"Source Services for this Policy: {services}")
    
    conn.close()

if __name__ == "__main__":
    check_latest_quote()
