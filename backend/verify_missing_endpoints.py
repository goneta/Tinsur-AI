import requests
import json

def check_missing_endpoints():
    try:
        response = requests.get("http://localhost:8000/openapi.json")
        response.raise_for_status()
        schema = response.json()
        paths = schema.get("paths", {})
        
        target_endpoints = [
            "/api/v1/notifications",
            "/api/v1/kyc/upload-and-parse"
        ]
        
        print(f"Total paths found: {len(paths)}")
        for te in target_endpoints:
            # Check for exact matches followed by potential query params or slashes
            matches = [p for p in paths if p.startswith(te)]
            if matches:
                 print(f"Endpoint {te}: FOUND - Matches: {matches}")
            else:
                 print(f"Endpoint {te}: MISSING")
                 
        # Print all paths starting with /api/v1/kyc
        kyc_paths = [p for p in paths if p.startswith("/api/v1/kyc")]
        print(f"KYC paths found: {kyc_paths}")
        
        # Print all paths starting with /api/v1/notifications
        notif_paths = [p for p in paths if p.startswith("/api/v1/notifications")]
        print(f"Notification paths found: {notif_paths}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_missing_endpoints()
