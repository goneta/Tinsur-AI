import requests

url = "http://localhost:8000/api/v1/auth/social/facebook"
data = {"token": "test-mock-token", "user_type": "client"}

try:
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.text}")
except Exception as e:
    print(f"Error: {e}")
