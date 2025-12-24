import requests
import sys

BASE_URL = "http://localhost:8000/api/v1"
LOGIN_URL = f"{BASE_URL}/auth/login"

def get_auth_token():
    try:
        response = requests.post(
            LOGIN_URL,
            json={"email": "admin@demoinsurance.com", "password": "Admin123!"},  # Adjust credentials if needed
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()["access_token"]
    except Exception as e:
        print(f"Login failed: {e}")
        try:
            print(response.text)
        except:
            pass
        sys.exit(1)

def test_sales_endpoints():
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    endpoints = [
        "/sales-reports/summary",
        "/sales-reports/by-channel",
        "/sales-reports/leaderboard"
    ]
    
    for endpoint in endpoints:
        url = f"{BASE_URL}{endpoint}"
        print(f"\n>>> TESTING {endpoint} <<<")
        try:
            response = requests.get(url, headers=headers)
            print(f"Status: {response.status_code}")
            if response.status_code != 200:
                print(f"FAILED: {response.text}")
            else:
                print("SUCCESS")
                print(f"Response: {response.text[:200]}") # Print first 200 chars
        except Exception as e:
            print(f"EXCEPTION: {e}")
        print("=" * 30)

if __name__ == "__main__":
    test_sales_endpoints()
