
import requests
import json
import time
import uuid

ORCHESTRATOR_URL = "http://localhost:8025/send-message"
ADMIN_URL = "http://localhost:8000/api/v1/admin"
API_KEY = "super-secret-a2a-key"

# Mocks
CLIENT_USER_ID = str(uuid.uuid4())
UNAUTHORIZED_USER_ID = str(uuid.uuid4())

def print_result(name, passed, detail=""):
    status = "[PASS]" if passed else "[FAIL]"
    print(f"{status} - {name}: {detail}")

def send_message(text, user_id=None):
    headers = {
        "Content-Type": "application/json",
        "X-API-KEY": API_KEY
    }
    payload = {
        "message": {
            "type": "user_text_message",
            "text": text
        },
        "context": {
            "user_id": user_id
        }
    }
    try:
        response = requests.post(ORCHESTRATOR_URL, json=payload, headers=headers, timeout=10)
        # We expect 200 even on permission denied from agent, but the content will say "Permission Denied"
        if response.status_code == 200:
            return response.json()
        return {"error": f"Status {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}

def verify_admin_access():
    print("\n--- Verifying Admin API Access ---")
    # This requires a valid token which is hard to mock here without logging in.
    # We will just hit the endpoint and expect 401 Unauthorized, which proves security is active.
    
    try:
        response = requests.get(f"{ADMIN_URL}/roles")
        print_result("Admin Endpoint Protection", 
                     response.status_code == 401, 
                     f"Got {response.status_code} (Expected 401)")
    except Exception as e:
        print_result("Admin Endpoint Protection", False, str(e))

def verify_security():
    print("--- Verifying Agent Security (RBAC) ---")
    
    # 1. Test: Quote Request with NO user_id (Should proceed if fallback allows, or fail if we enforced strictness)
    print("\n--- Test 1: Anonymous Access (Fallback) ---")
    res = send_message("I need a quote", user_id=None)
    # Refinement: In strict mode this should fail, but I left it open in implementation for now.
    print_result("Anonymous", "premium_monthly" in json.dumps(res), "Quote generated (Fallback)")

    # 2. Test: Context Passing
    print("\n--- Test 2: Unknown User (Should Deny) ---")
    res_deny = send_message("I need a quote", user_id=UNAUTHORIZED_USER_ID)
    text_deny = json.dumps(res_deny)
    
    # NOTE: Since we haven't updated the Agents to USE SecurityService yet (Task #2 in task.md is NOT done),
    # this test will likely FAIL (it will still generate a quote).
    # This confirms Task #2 is needed.
    
    print_result("Permission Check (Agent)", 
                 "permission" in text_deny.lower() and "sorry" in text_deny.lower(), 
                 f"Response: {text_deny[:100]}...")
                 
    verify_admin_access()

    # 3. Test: Granular Permission Enforcement (Mocking Context)
    # To test this without full end-to-end login, we can use the send_message helper 
    # but manually construct the 'context' payload to simulate what the Chat Endpoint would send.
    # The Chat Endpoint sends: {"user_id": ..., "role": ..., "permissions": [...]}
    
    print("\n--- Test 3: Permission Enforcement (Mocked Context) ---")
    
    # Case A: User WITH quote permission
    user_with_quote_perm = {
        "user_id": str(uuid.uuid4()),
        "user_role": "agent",
        "permissions": ["quote:read"]
    }
    # We cheat a bit: send_message takes user_id, but we want to pass full dict. 
    # But wait, send_message puts the 'user_id' arg into `context: { user_id: ... }`.
    # The agent executor expects `metadata` (which IS the context dict) to contain `permissions`.
    # So we need to modify send_message? Or just make a new helper.
    
    def send_message_custom_context(text, context_dict):
        headers = { "Content-Type": "application/json", "X-API-KEY": API_KEY }
        payload = {
            "message": { "type": "user_text_message", "text": text },
            "context": context_dict
        }
        try:
            return requests.post(ORCHESTRATOR_URL, json=payload, headers=headers, timeout=10).json()
        except Exception as e:
            return {"error": str(e)}

    # A: Allow Quote
    res_a = send_message_custom_context("I need a quote", user_with_quote_perm)
    res_text_a = json.dumps(res_a)
    print_result("Allow Quote", "Routing request to Quote Specialist" in res_text_a, "Should allow")
    
    # B: Deny Quote (No perms)
    user_no_perms = {
        "user_id": str(uuid.uuid4()),
        "user_role": "client",
        "permissions": []
    }
    res_b = send_message_custom_context("I need a quote", user_no_perms)
    res_text_b = json.dumps(res_b)
    print_result("Deny Quote", "do not have permission" in res_text_b, "Should deny")

    # C: Allow Claim
    user_with_claim_perm = {
        "user_id": str(uuid.uuid4()),
        "user_role": "adjuster",
        "permissions": ["claim:read"]
    }
    res_c = send_message_custom_context("I want to file a claim", user_with_claim_perm)
    res_text_c = json.dumps(res_c)
    print_result("Allow Claim", "Routing request to Claims Specialist" in res_text_c, "Should allow")

if __name__ == "__main__":
    verify_security()
