import requests

base_url = "http://127.0.0.1:8000/api/v1"

def test_api():
    try:
        # We don't have a token easily, but we can check if it returns 401 or 404
        # If it returns 401, the endpoint exists.
        # If it returns 404, the endpoint doesn't exist.
        
        r = requests.get(f"{base_url}/admin/roles")
        print(f"Roles status: {r.status_code}")
        
        r = requests.get(f"{base_url}/admin/permissions")
        print(f"Permissions status: {r.status_code}")
        
        r = requests.get(f"{base_url}/admin/ping")
        print(f"Ping status: {r.status_code}")
        if r.status_code == 200:
            print(f"Ping response: {r.json()}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_api()
