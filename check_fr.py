import requests
import json

try:
    response = requests.get("http://localhost:8000/api/v1/translations/?language_code=fr")
    response.raise_for_status()
    data = response.json()
    
    if "fr" in data:
        keys = list(data["fr"].keys())
        print(f"Total keys: {len(keys)}")
        if "portal.policy_label" in data["fr"]:
            print(f"portal.policy_label: {data['fr']['portal.policy_label']}")
        else:
            print("portal.policy_label NOT FOUND")
            
        # Print first 5 keys
        print("First 5 keys:", keys[:5])
    else:
        print("Key 'fr' not found in response")
        print(data.keys())

except Exception as e:
    print(f"Error: {e}")
