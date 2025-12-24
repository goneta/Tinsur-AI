
import requests
import sys

urls = [
    "http://127.0.0.1:8000/health",
    "http://localhost:8000/health",
    "http://127.0.0.1:8019/", # Claims agent root might not be health, but check connectivity
]

print("Verifying HTTP Connectivity...")

for url in urls:
    try:
        print(f"Checking {url}...")
        response = requests.get(url, timeout=2)
        print(f"✅ {url} responded with {response.status_code}")
        print(f"   Response: {response.text[:50]}")
    except Exception as e:
        print(f"❌ {url} FAILED: {e}")
