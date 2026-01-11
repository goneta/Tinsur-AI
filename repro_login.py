import requests
import json

url = "http://localhost:8000/api/v1/auth/login"
payload = {
    "email": "test_client@tinsur.ai",
    "password": "Password123!"
}
headers = {
    "Content-Type": "application/json"
}

try:
    print(f"Attempting login to {url}...")
    response = requests.post(url, json=payload, headers=headers, timeout=10)
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.text}")
except Exception as e:
    print(f"Error during request: {type(e).__name__}: {e}")
