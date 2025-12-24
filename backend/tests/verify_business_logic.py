
import requests
import json
import time

API_KEY = "super-secret-a2a-key"
HEADERS = {
    "Content-Type": "application/json",
    "X-API-KEY": API_KEY
}

def call_agent(url_port, text):
    url = f"http://localhost:{url_port}/send-message"
    payload = {
        "message": {
            "type": "user_text_message",
            "text": text
        }
    }
    try:
        response = requests.post(url, json=payload, headers=HEADERS, timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def test_enhanced_logic():
    print("\n--- Testing Quote Agent (8020) ---")
    # 1. Quote Agent: Auto
    res = call_agent(8020, "Quote for my car value 30000")
    print(f"Quote Response (Auto): {json.dumps(res, indent=2)}")
    
    # 2. Quote Agent: JSON
    json_req = json.dumps({"policy_type": "home", "value": 500000})
    res_json = call_agent(8020, json_req)
    print(f"Quote Response (JSON): {json.dumps(res_json, indent=2)}")

    print("\n--- Testing Claims Agent (8019) ---")
    # 3. Claims Agent: High Fraud
    res_claim = call_agent(8019, "Stolen jewelry value 10000")
    print(f"Claim Response (Fraud): {json.dumps(res_claim, indent=2)}")

    print("\n--- Testing Policy Agent (8021) ---")
    # 4. Policy Agent: With Quote
    res_policy = call_agent(8021, "Create policy from quote Q-123456")
    print(f"Policy Response: {json.dumps(res_policy, indent=2)}")

if __name__ == "__main__":
    time.sleep(2)
    test_enhanced_logic()
