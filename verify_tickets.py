import requests
import sys

BASE_URL = "http://localhost:8000/api/v1"
PORTAL_URL = "http://localhost:8000/api/v1/portal"

def login_admin():
    # Assuming default admin from init_db
    resp = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "admin@demoinsurance.com",
        "password": "Admin123!"
    })
    if resp.status_code != 200:
        print("Failed to login admin:", resp.text)
        sys.exit(1)
    return resp.json()["access_token"]

def register_client():
    # Register a new client for testing
    import uuid
    email = f"test_client_{uuid.uuid4().hex[:6]}@example.com"
    data = {
        "email": email,
        "password": "password123",
        "first_name": "Test",
        "last_name": "Client",
        "phone": "+1234567890",
        "subdomain": "demo" 
    }
    
    # We need a valid company ID. Let's get it from admin?
    admin_token = login_admin()
    headers = {"Authorization": f"Bearer {admin_token}"}
    me = requests.get(f"{BASE_URL}/auth/me", headers=headers).json()
    company_id = me["company_id"]
    
    data["company_id"] = company_id
    
    resp = requests.post(f"{PORTAL_URL}/register", json=data)
    if resp.status_code != 200:
        print("Failed to register client:", resp.text)
        sys.exit(1)
        
    # Login client
    resp = requests.post(f"{BASE_URL}/auth/login", json={
        "email": email,
        "password": "password123"
    })
    return resp.json()["access_token"], company_id

def run_test():
    print("1. Logging in Admin...")
    admin_token = login_admin()
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    print("   Admin logged in.")
    
    print("2. Registering/Logging in Client...")
    client_token, company_id = register_client()
    client_headers = {"Authorization": f"Bearer {client_token}"}
    print("   Client logged in.")
    
    print("3. Client creates ticket...")
    ticket_payload = {
        "subject": "Test Ticket Issue",
        "category": "technical",
        "description": "I cannot access my policy.",
        "priority": "high",
        "client_id": None # Schema might expect this but portal endpoint injects it?
        # Portal endpoint uses TicketCreate schema which has client_id optional
        # but the endpoint ignores it and uses current_client.id
    }
    resp = requests.post(f"{PORTAL_URL}/tickets", json=ticket_payload, headers=client_headers)
    if resp.status_code != 200:
        print("Failed to create ticket:", resp.text)
        sys.exit(1)
    ticket = resp.json()
    ticket_id = ticket["id"]
    print(f"   Ticket created: {ticket['ticket_number']}")
    
    print("4. Admin lists tickets...")
    resp = requests.get(f"{BASE_URL}/tickets/", headers=admin_headers)
    tickets = resp.json()
    found = next((t for t in tickets if t["id"] == ticket_id), None)
    if not found:
        print("Error: Admin did not find the ticket.")
        sys.exit(1)
    print("   Admin found the ticket.")
    
    print("5. Admin replies...")
    reply_payload = {
        "message": "We are looking into it.",
        "is_internal": False,
        "sender_type": "user"
    }
    resp = requests.post(f"{BASE_URL}/tickets/{ticket_id}/reply", json=reply_payload, headers=admin_headers)
    if resp.status_code != 200:
        print("Failed to admin reply:", resp.text)
        sys.exit(1)
    print("   Admin replied.")
    
    print("6. Client checks ticket details...")
    resp = requests.get(f"{PORTAL_URL}/tickets/{ticket_id}", headers=client_headers)
    client_view = resp.json()
    messages = client_view.get("messages", [])
    if len(messages) < 1:
         print("Error: Client sees no messages.")
         sys.exit(1)
    if messages[0]["message"] != "We are looking into it.":
         print("Error: Message content mismatch.")
         print(messages)
         sys.exit(1)
    print("   Client sees the reply.")
    
    print("7. Client replies...")
    client_reply = {"message": "Thank you, please hurry.", "sender_type": "client"}
    resp = requests.post(f"{PORTAL_URL}/tickets/{ticket_id}/reply", json=client_reply, headers=client_headers)
    if resp.status_code != 200:
        print("Failed to client reply:", resp.text)
        sys.exit(1)
    print("   Client replied.")
    
    print("8. Admin checks internal note...")
    # Admin adds internal note
    note_payload = {
        "message": "User is impatient.",
        "is_internal": True,
        "sender_type": "user"
    }
    requests.post(f"{BASE_URL}/tickets/{ticket_id}/reply", json=note_payload, headers=admin_headers)
    
    # Client shouldn't see it (though endpoint filters it? lets check logic)
    # Portal endpoint logic: `!msg.is_internal && ...` in Frontend loop?
    # Backend portal endpoint simply returns `Ticket` which includes `messages`.
    # Wait, does the backend serializer filter it?
    # schemas.Ticket uses TicketMessage which has is_internal.
    # The Portal API endpoint returns the full Ticket object with messages list.
    # Backend doesn't filter `is_internal` in the relationship load.
    # SO CLIENT API RECEIVES INTERNAL NOTES! ATTENTION!
    # I need to fix this in backend `portal.py` get_ticket!
    
    print("   (Verification Note: We need to ensure client doesn't receive internal notes in API)")
    resp = requests.get(f"{PORTAL_URL}/tickets/{ticket_id}", headers=client_headers)
    client_msgs = resp.json()["messages"]
    internal_found = any(m["is_internal"] for m in client_msgs)
    if internal_found:
        print("SECURITY FAIL: Client received internal note!")
    else:
        print("   Client did not receive internal note (if filtering implemented).")

if __name__ == "__main__":
    run_test()
