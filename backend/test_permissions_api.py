
import requests
import sys

def test_api():
    print("Testing Permissions API...")
    try:
        # Test Roles
        print("Fetching Roles...")
        r = requests.get("http://localhost:8000/api/v1/permissions/roles", timeout=5)
        print(f"Roles Status: {r.status_code}")
        if r.status_code == 200:
            print(f"Roles Count: {len(r.json())}")
        else:
            print(f"Roles Error: {r.text}")

        # Test Permissions
        print("\nFetching Permissions...")
        r = requests.get("http://localhost:8000/api/v1/permissions/permissions", timeout=5)
        print(f"Permissions Status: {r.status_code}")
        if r.status_code == 200:
            print(f"Permissions Count: {len(r.json())}")
        else:
            print(f"Permissions Error: {r.text}")
            
    except Exception as e:
        print(f"Request Failed: {e}")

if __name__ == "__main__":
    test_api()
