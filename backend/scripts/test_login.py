
import requests
import json

# URL based on router analysis
LOGIN_URL = "http://localhost:8000/api/v1/auth/login/access-token"
# Note: FastAPI OAuth2RequestForm usually expects form-data, not JSON, but let's check
# Or it might be /api/v1/auth/login 

# Let's try both common patterns
url_alternatives = [
    "http://localhost:8000/api/v1/auth/login/access-token",
    "http://localhost:8000/api/v1/login/access-token",
    "http://localhost:8000/api/v1/auth/token"
]

payload = {
    "username": "admin@example.com",
    "password": "password"
}

print("Testing Authentication Endpoint...")

success = False
for url in url_alternatives:
    try:
        print(f"Trying {url} (as Form Data)...")
        # FastAPI OAuth2PasswordRequestForm expects data=...
        response = requests.post(url, data=payload, timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:100]}")
        
        if response.status_code != 404:
            success = True
            if response.status_code == 200:
                print("✅ Login Successful!")
            else:
                print("⚠️ Login Failed (but endpoint exists)")
            break
            
    except Exception as e:
        print(f"❌ Connection Failed to {url}: {e}")

if not success:
    print("Could not find a working login endpoint or connect to it.")
