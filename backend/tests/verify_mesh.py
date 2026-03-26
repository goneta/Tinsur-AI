
import requests
import json
import time

ORCHESTRATOR_URL = "http://localhost:8025/send-message"
API_KEY = "super-secret-a2a-key" # Default key

def print_result(name, passed, detail=""):
    status = "[PASS]" if passed else "[FAIL]"
    msg = f"{status} - {name}: {detail}"
    print(msg)
    with open("mesh_results.txt", "a", encoding="utf-8") as f:
        f.write(msg + "\n")
        if not passed:
             f.write(f"DEBUG RESPONSE: {detail}\n")

def check_port(port):
    try:
        # Just check if we can connect; endpoint might not exist for root but socket connect works
        # Using a get to /docs assuming FastAPI/Starlette often has it, or just connection check
        requests.get(f"http://localhost:{port}/", timeout=1)
        return True
    except Exception:
        return False

def send_message(text):
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
            "user_id": "34f1620d-9c7b-4cdf-a0c5-500aacad5cfd5",
            "user_role": "super_admin"
        }
    }
    try:
        response = requests.post(ORCHESTRATOR_URL, json=payload, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
        return {"error": f"Status {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}

def verify_mesh():
    print("--- Verifying Agent Mesh Connectivity ---")
    
    # 1. Check Ports
    ports = [8025, 8019, 8020, 8021]
    all_ports_up = True
    for port in ports:
        if not check_port(port):
            print_result(f"Port {port}", False, "Connection Refused")
            all_ports_up = False
    
    if not all_ports_up:
        print("❌ Not all agents are running. Aborting.")
        return

    print_result("Agent Ports", True, "All agents reachable")

    # 2. Test Delegation: Quote
    print("\n--- Testing Delegation: Quote ---")
    res_quote = send_message("I need a car insurance quote")
    text_quote = json.dumps(res_quote)
    passed_quote = "Quote Specialist" in text_quote
    print_result("Orchestrator -> Quote", passed_quote, text_quote if not passed_quote else "Detected routing")

    # 3. Test Delegation: Claims
    print("\n--- Testing Delegation: Claims ---")
    res_claim = send_message("I need to file a claim for a crash")
    text_claim = json.dumps(res_claim)
    passed_claim = "Claims Specialist" in text_claim
    print_result("Orchestrator -> Claims", passed_claim, text_claim if not passed_claim else "Detected routing")
    
    # 4. Test Delegation: Policy
    print("\n--- Testing Delegation: Policy ---")
    res_policy = send_message("Create a policy for me")
    text_policy = json.dumps(res_policy)
    passed_policy = "Policy Specialist" in text_policy
    print_result("Orchestrator -> Policy", passed_policy, text_policy if not passed_policy else "Detected routing")

    # 5. Test Delegation: Memory
    print("\n--- Testing Delegation: Memory ---")
    res_memory = send_message("Remember that I am a VIP client")
    text_memory = json.dumps(res_memory)
    # Check if a2a_persistent_storage_agent mentioned "Context Saved"
    passed_memory = "Context Saved" in text_memory or "Long-term Memory" in text_memory
    print_result("Orchestrator -> Memory", passed_memory, text_memory if not passed_memory else "Detected routing/storage")

if __name__ == "__main__":
    verify_mesh()
