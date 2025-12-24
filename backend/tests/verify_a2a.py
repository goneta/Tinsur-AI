
import requests
import json
import time

def test_orchestrator_delegation():
    url = "http://localhost:8025/send-message"
    headers = {
        "Content-Type": "application/json",
        "X-API-KEY": "super-secret-a2a-key"
    }
    
    # payload to trigger quote delegation
    payload = {
        "message": {
            "type": "user_text_message",
            "text": "I need a quote for my car"
        }
    }
    
    print("Sending request to Orchestrator...")
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            print("Response Response:", response.json())
        else:
            print(f"Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    # Wait for servers to start
    time.sleep(5) 
    test_orchestrator_delegation()
