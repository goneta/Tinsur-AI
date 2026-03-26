
import requests
import json
import time
import uuid

ORCHESTRATOR_URL = "http://localhost:8025/send-message"
PERSISTENCE_URL = "http://localhost:8031/send-message"
API_KEY = "super-secret-a2a-key"

def test_persistence_direct():
    print("--- Testing Persistence Agent Directly ---")
    headers = {"Content-Type": "application/json", "X-API-KEY": API_KEY}
    
    # 1. Save something
    unique_fact = f"I love coding at {time.time()}"
    payload_save = {
        "message": {"type": "user_text_message", "text": f"remember that {unique_fact}"},
        "context": {"user_id": "34f1620d-9c7b-4cdf-a0c5-00aacad5cfd5"}
    }
    
    try:
        res_save = requests.post(PERSISTENCE_URL, json=payload_save, headers=headers, timeout=5)
        print(f"Save Response: {res_save.status_code}")
        print(res_save.text)
        
        # 2. Retrieve it
        payload_load = {
            "message": {"type": "user_text_message", "text": "what do you remember"},
            "context": {"user_id": "34f1620d-9c7b-4cdf-a0c5-00aacad5cfd5"}
        }
        res_load = requests.post(PERSISTENCE_URL, json=payload_load, headers=headers, timeout=5)
        print(f"Load Response: {res_load.status_code}")
        data = res_load.json()
        print(json.dumps(data, indent=2))
        
        success = unique_fact in str(data)
        print(f"VERIFICATION: {'PASS' if success else 'FAIL'}")
        
    except Exception as e:
        print(f"ERROR: {str(e)}")

if __name__ == "__main__":
    test_persistence_direct()
