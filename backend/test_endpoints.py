#!/usr/bin/env python
"""Test Tinsur-AI API endpoints"""

import requests
import time
import json

# Give server time to start
time.sleep(2)

BASE_URL = "http://127.0.0.1:8000"

print("="*50)
print("TESTING TINSUR-AI API ENDPOINTS")
print("="*50)
print(f"\nBase URL: {BASE_URL}\n")

# Test 1: Swagger UI
print("Test 1: Swagger UI")
print("-" * 30)
try:
    response = requests.get(f"{BASE_URL}/docs", timeout=5)
    if response.status_code == 200:
        print("[PASS] Swagger UI accessible (200)")
    else:
        print(f"[FAIL] Status code: {response.status_code}")
except Exception as e:
    print(f"[FAIL] Error: {e}")

print()

# Test 2: OpenAPI Schema
print("Test 2: OpenAPI Schema")
print("-" * 30)
try:
    response = requests.get(f"{BASE_URL}/openapi.json", timeout=5)
    if response.status_code == 200:
        spec = response.json()
        path_count = len(spec.get("paths", {}))
        print(f"[PASS] OpenAPI schema accessible")
        print(f"       Total paths: {path_count}")
        print(f"       API Title: {spec.get('info', {}).get('title', 'N/A')}")
        print(f"       API Version: {spec.get('info', {}).get('version', 'N/A')}")
        
        # Show quote endpoints
        print("\n       Quote-related endpoints:")
        for path in spec.get("paths", {}):
            if "quote" in path.lower():
                methods = list(spec["paths"][path].keys())
                print(f"         {methods} {path}")
    else:
        print(f"[FAIL] Status code: {response.status_code}")
except Exception as e:
    print(f"[FAIL] Error: {e}")

print()

# Test 3: Health Check
print("Test 3: Health/Status")
print("-" * 30)
try:
    response = requests.get(f"{BASE_URL}/api/v1/health", timeout=5)
    print(f"[INFO] Health endpoint status: {response.status_code}")
    if response.status_code == 200:
        print(f"       Response: {response.json()}")
except Exception as e:
    print(f"[INFO] Health endpoint not available: {type(e).__name__}")

print()
print("="*50)
print("BACKEND TESTING COMPLETE")
print("="*50)
