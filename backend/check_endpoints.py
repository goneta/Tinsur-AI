import requests
import json
import sys

def check_endpoints():
    try:
        response = requests.get("http://localhost:8000/openapi.json")
        response.raise_for_status()
        schema = response.json()
        paths = schema.get("paths", {})
        
        expected = [
            "/api/v1/tickets/",
            "/api/v1/referrals/",
            "/api/v1/loyalty/{client_id}",
            "/api/v1/telematics/",
            "/api/v1/ml-models/"
        ]
        
        print(f"Total paths found: {len(paths)}")
        for e in expected:
            found = any(p for p in paths if e in p) # flexible match
            print(f"Endpoint {e}: {'FOUND' if found else 'MISSING'}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_endpoints()
