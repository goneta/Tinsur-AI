import requests
import json

try:
    response = requests.get("http://localhost:8000/api/v1/translations/?language_code=fr")
    response.raise_for_status()
    data = response.json()
    
    if "fr" in data:
        portal_keys = [k for k in data["fr"].keys() if k.startswith("portal.")]
        print(f"Total portal keys: {len(portal_keys)}")
        for k in portal_keys:
            print(f"{k}: {data['fr'][k]}")
            
    else:
        print("Key 'fr' not found in response")

except Exception as e:
    print(f"Error: {e}")
