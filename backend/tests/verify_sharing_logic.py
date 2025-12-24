
import requests
import sys

# Constants
BASE_URL = "http://localhost:8000/api/v1"
ADMIN_EMAIL = "admin@demoinsurance.com"
ADMIN_PASSWORD = "Admin123!"

MANAGER_EMAIL = "manager_test@demo.com"
CLIENT_EMAIL = "client_test@demo.com"
PASSWORD = "Password123!"

def login(email, password):
    response = requests.post(f"{BASE_URL}/auth/login", json={"email": email, "password": password})
    if response.status_code != 200:
        print(f"Login failed for {email}: {response.text}")
        return None
    return response.json()["access_token"]

def create_user(admin_token, email, role, first_name):
    # Try creating, ignore if exists
    headers = {"Authorization": f"Bearer {admin_token}"}
    payload = {
        "email": email,
        "password": PASSWORD,
        "role": role,
        "first_name": first_name,
        "last_name": "TestUser",
        "company_id": "00000000-0000-0000-0000-000000000000" # Dummy, backend will override with admin's company
    }
    response = requests.post(f"{BASE_URL}/users/", json=payload, headers=headers)
    if response.status_code == 200:
        print(f"Created user {role}: {email}")
    elif response.status_code == 400 and "already exists" in response.text:
        print(f"User {role} already exists.")
    else:
        print(f"Failed to create user {role}: {response.text}")

def upload_doc(token, filename, visibility, scope):
    # 1. Upload
    headers = {"Authorization": f"Bearer {token}"}
    files = {'file': (filename, 'dummy content', 'text/plain')}
    data = {'label': 'Document'}
    
    print(f"\nUploading {filename}...")
    resp = requests.post(f"{BASE_URL}/documents/upload", headers=headers, files=files, data=data)
    if resp.status_code != 200:
        print("Upload failed")
        return None
    
    doc_id = resp.json()["document_id"]
    
    # 2. Set Sharing Settings
    payload = {
        "visibility": visibility,
        "scope": scope,
        "is_shareable": True,
        "reshare_rule": "C"
    }
    resp = requests.post(f"{BASE_URL}/documents/{doc_id}/share", json=payload, headers=headers)
    if resp.status_code == 200:
        print(f"Set settings: Visibility={visibility}, Scope={scope}")
    else:
        print(f"Failed to set settings: {resp.text}")
        
    return doc_id

def check_visibility(token, doc_id, user_role):
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(f"{BASE_URL}/documents/list", headers=headers)
    if resp.status_code != 200:
        print(f"List failed for {user_role}")
        return False
        
    data = resp.json()
    # Check all docs (my_docs, shared_with_me, public_docs)
    # Since we are checking broadcast visibility, it should appear in 'shared_with_me' usually or 'public_docs' if public
    # But wait, logic puts broadcast into 'shared_with_me'.
    
    found = False
    for category in data.values():
        for doc in category:
            if doc['id'] == doc_id:
                found = True
                break
    
    if found:
        print(f"SUCCESS: {user_role} CAN see the document.")
    else:
        print(f"INFO: {user_role} CANNOT see the document.")
    return found

def run():
    # 1. Admin Login
    print("--- 1. Admin Login ---")
    admin_token = login(ADMIN_EMAIL, ADMIN_PASSWORD)
    if not admin_token: return

    # 2. Create Test Users
    print("\n--- 2. Creating Test Users ---")
    create_user(admin_token, MANAGER_EMAIL, "manager", "Manager")
    create_user(admin_token, CLIENT_EMAIL, "client", "Client")
    
    # 3. Login as Test Users
    manager_token = login(MANAGER_EMAIL, PASSWORD)
    client_token = login(CLIENT_EMAIL, PASSWORD)
    
    if not manager_token or not client_token:
        print("Failed to login test users")
        return

    # Scenario A: B2B Document (Manager YES, Client NO)
    print("\n--- Scenario A: B2B Document ---")
    # To test broadcast, we need a doc from DIFFERENT company.
    # Current setup puts all users in SAME company usually?
    # Wait, 'create_admin.py' makes one company. 'register_user' creates new company only if requested.
    # Our 'create_user' endpoint assigns to Admin's company.
    # Logic in documents.py: 
    # broadcast_query = db.query(Document).filter(Document.company_id != current_user.company_id, ...)
    # IF Manager and Client are in SAME company as Admin, they will NOT see it via Broadcast logic (it's internal).
    # They should see it in 'my_docs' if company-wide sharing is implied, OR 'shared_with_me' if explicitly shared.
    
    # CRITICAL: If they are same company, `list_documents` logic for "Shared With Me" logic I wrote:
    # `Document.company_id != current_user.company_id`
    # So internal B2B/B2C sharing logic is missing from my update?
    # Yes, I implemented Inter-Company broadcast. 
    # Internal sharing usually relies on `my_docs = filter(company_id == user.company_id)`.
    # Currently `my_docs` returns ALL company docs to everyone in that company.
    # So Manager and Client ALREADY see everything internal.
    
    # FIX: I need to verify INTER-COMPANY visibility.
    # So I need to create a SECOND COMPANY and a user in it.
    
    print("\n--- Setup: Creating External Company/User ---")
    # Register a new user with a new company
    reg_payload = {
        "email": "external_admin@corp2.com",
        "password": "Password123!",
        "first_name": "Ext",
        "last_name": "Admin",
        "company_name": "Corp 2",
        "company_subdomain": "corp2"
    }
    
    # Assuming public registration endpoint exists
    resp = requests.post(f"{BASE_URL}/auth/register", json=reg_payload)
    if resp.status_code == 200 or (resp.status_code == 400 and "registered" in resp.text):
        print("External Company Admin registered.")
    else:
        print(f"External Reg Failed: {resp.text}")
        return

    ext_token = login("external_admin@corp2.com", "Password123!")
    
    # Now External Admin uploads a doc (Company 2)
    doc_id_b2b = upload_doc(ext_token, "b2b_contract.txt", "PRIVATE", "B2B")
    
    print("\nChecking Visibility (Expected: Manager=YES, Client=NO)")
    check_visibility(manager_token, doc_id_b2b, "Manager (Company 1)") # Should be YES
    check_visibility(client_token, doc_id_b2b, "Client (Company 1)")   # Should be NO
    
    # Scenario B: B2C Document (Manager YES, Client YES)
    print("\n--- Scenario B: B2C Document ---")
    doc_id_b2c = upload_doc(ext_token, "public_announcement.txt", "PRIVATE", "B2C")
    
    print("\nChecking Visibility (Expected: Manager=YES, Client=YES)")
    check_visibility(manager_token, doc_id_b2c, "Manager (Company 1)")
    check_visibility(client_token, doc_id_b2c, "Client (Company 1)")

if __name__ == "__main__":
    run()
