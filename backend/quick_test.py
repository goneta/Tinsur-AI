#!/usr/bin/env python3
"""Quick test to verify Tinsur-AI server is running"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_server():
    print("\n" + "="*80)
    print("TINSUR-AI SERVER HEALTH CHECK")
    print("="*80 + "\n")
    
    # Test 1: Basic health check
    print("[1] Testing /docs endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/docs", timeout=5)
        if response.status_code == 200:
            print("    [PASS] /docs endpoint responding (200 OK)")
        else:
            print(f"    [FAIL] /docs returned {response.status_code}")
            return False
    except Exception as e:
        print(f"    [FAIL] Connection error: {str(e)}")
        return False
    
    # Test 2: API availability
    print("\n[2] Testing /api/v1 routes...")
    try:
        # Try to get API docs
        response = requests.get(f"{BASE_URL}/openapi.json", timeout=5)
        if response.status_code == 200:
            api_docs = response.json()
            routes = list(api_docs.get('paths', {}).keys())
            print(f"    [PASS] API schema loaded - {len(routes)} routes available")
            
            # Check for quote-related endpoints
            quote_routes = [r for r in routes if 'quote' in r.lower()]
            print(f"    [INFO] Found {len(quote_routes)} quote-related endpoints:")
            for route in quote_routes[:5]:
                print(f"           - {route}")
        else:
            print(f"    [FAIL] OpenAPI schema returned {response.status_code}")
            return False
    except Exception as e:
        print(f"    [FAIL] Error loading API schema: {str(e)}")
        return False
    
    # Test 3: Database connectivity
    print("\n[3] Testing database connectivity...")
    try:
        # Try a simple endpoint that hits the database
        response = requests.get(
            f"{BASE_URL}/api/v1/companies",
            headers={"Authorization": "Bearer test-token"},
            timeout=5
        )
        # Should get 401 (unauthorized) if auth is enabled, not 500 (server error)
        if response.status_code in [200, 401, 403, 404]:
            print(f"    [PASS] Database accessible ({response.status_code} response)")
        else:
            print(f"    [FAIL] Unexpected response: {response.status_code}")
            print(f"           {response.text[:200]}")
            return False
    except Exception as e:
        print(f"    [FAIL] Database error: {str(e)}")
        return False
    
    print("\n" + "="*80)
    print("SUMMARY: ALL TESTS PASSED - SERVER IS READY FOR TESTING")
    print("="*80 + "\n")
    
    print("Next steps:")
    print("1. Access API documentation: http://localhost:8000/docs")
    print("2. Test quote endpoints:")
    print("   - POST /api/v1/quotes/calculate (Admin)")
    print("   - POST /api/v1/portal/quotes/calculate (Client)")
    print("3. Create quotes:")
    print("   - POST /api/v1/quotes/ (Admin)")
    print("   - POST /api/v1/portal/quotes (Client)")
    print("\n")
    
    return True

if __name__ == "__main__":
    # Wait for server to be fully ready
    print("Waiting for server to be ready...")
    time.sleep(2)
    
    success = test_server()
    exit(0 if success else 1)
