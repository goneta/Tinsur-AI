#!/usr/bin/env python
"""Test quote parity between admin and client portal endpoints"""

import requests
import json
import time
from decimal import Decimal

BASE_URL = "http://127.0.0.1:8000"

# Load test tokens from generated file
import os
import json

def load_tokens():
    """Load test tokens from test_tokens.json"""
    try:
        with open("test_tokens.json", "r") as f:
            tokens = json.load(f)
            return tokens.get("admin_token"), tokens.get("client_token")
    except FileNotFoundError:
        print("[WARNING] test_tokens.json not found. Run generate_test_tokens.py first.")
        return None, None

ADMIN_TOKEN, CLIENT_TOKEN = load_tokens()

# Test scenarios for quote parity
TEST_SCENARIOS = [
    {
        "name": "Standard Auto Insurance",
        "params": {
            "policy_type_id": "auto_premium",
            "coverage_amount": 100000,
            "duration_months": 12,
            "risk_factors": {
                "age": 35,
                "driving_record": "clean",
                "vehicle_type": "sedan",
                "annual_miles": 15000
            }
        }
    },
    {
        "name": "High-Risk Young Driver",
        "params": {
            "policy_type_id": "auto_premium",
            "coverage_amount": 250000,
            "duration_months": 6,
            "risk_factors": {
                "age": 22,
                "driving_record": "accidents",
                "vehicle_type": "sports_car",
                "annual_miles": 25000
            }
        }
    },
    {
        "name": "Low-Risk Experienced Driver",
        "params": {
            "policy_type_id": "auto_premium",
            "coverage_amount": 50000,
            "duration_months": 24,
            "risk_factors": {
                "age": 55,
                "driving_record": "clean",
                "vehicle_type": "suv",
                "annual_miles": 8000
            }
        }
    },
    {
        "name": "Minimum Coverage",
        "params": {
            "policy_type_id": "auto_standard",
            "coverage_amount": 10000,
            "duration_months": 1,
            "risk_factors": {
                "age": 40,
                "driving_record": "clean",
                "vehicle_type": "sedan"
            }
        }
    },
    {
        "name": "Maximum Coverage",
        "params": {
            "policy_type_id": "auto_premium",
            "coverage_amount": 1000000,
            "duration_months": 36,
            "risk_factors": {
                "age": 50,
                "driving_record": "clean",
                "vehicle_type": "luxury",
                "annual_miles": 5000
            }
        }
    }
]

def check_backend():
    """Verify backend is running"""
    print("Checking backend connectivity...")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"[OK] Backend is running: {data.get('name')} v{data.get('version')}")
            return True
    except Exception as e:
        print(f"[ERROR] Backend not responding: {e}")
        return False

def test_parity():
    """Run quote parity tests"""
    
    print("\n" + "=" * 60)
    print("TINSUR-AI QUOTE PARITY TEST SUITE")
    print("=" * 60)
    print()
    
    # Check backend
    if not check_backend():
        print("\nERROR: Backend is not running. Start it first:")
        print("  python run_server.py")
        return False
    
    print()
    
    results = []
    
    for idx, scenario in enumerate(TEST_SCENARIOS, 1):
        print(f"\n[{idx}/{len(TEST_SCENARIOS)}] Testing: {scenario['name']}")
        print("-" * 60)
        
        try:
            # Admin endpoint (with JWT token)
            admin_response = requests.post(
                f"{BASE_URL}/api/v1/quotes/calculate",
                headers={
                    "Authorization": f"Bearer {ADMIN_TOKEN}"
                } if ADMIN_TOKEN else {},
                json={
                    "client_id": "test_client_001",
                    **scenario['params']
                },
                timeout=10
            )
            
            # Client portal endpoint (with JWT token)
            client_response = requests.post(
                f"{BASE_URL}/api/v1/portal/quotes/calculate",
                headers={
                    "Authorization": f"Bearer {CLIENT_TOKEN}"
                } if CLIENT_TOKEN else {},
                json=scenario['params'],
                timeout=10
            )
            
            # Check responses
            if admin_response.status_code != 200:
                print(f"âœ— Admin endpoint error: {admin_response.status_code}")
                print(f"  Response: {admin_response.text[:200]}")
                results.append({
                    "scenario": scenario['name'],
                    "status": "FAIL",
                    "reason": f"Admin API error: {admin_response.status_code}"
                })
                continue
            
            if client_response.status_code != 200:
                print(f"âœ— Client endpoint error: {client_response.status_code}")
                print(f"  Response: {client_response.text[:200]}")
                results.append({
                    "scenario": scenario['name'],
                    "status": "FAIL",
                    "reason": f"Client API error: {client_response.status_code}"
                })
                continue
            
            admin_data = admin_response.json()
            client_data = client_response.json()
            
            print(f"âœ“ Both endpoints responded successfully")
            
            # Compare critical fields
            critical_fields = [
                "base_premium",
                "subtotal",
                "final_price",
                "validity_days"
            ]
            
            mismatches = []
            
            for field in critical_fields:
                admin_val = admin_data.get(field)
                client_val = client_data.get(field)
                
                # Handle numeric comparison with tolerance
                if isinstance(admin_val, (int, float)) and isinstance(client_val, (int, float)):
                    admin_decimal = Decimal(str(admin_val))
                    client_decimal = Decimal(str(client_val))
                    match = abs(admin_decimal - client_decimal) < Decimal("0.01")
                else:
                    match = admin_val == client_val
                
                status = "âœ“" if match else "âœ—"
                print(f"  {status} {field}: {admin_val} (admin) vs {client_val} (client)")
                
                if not match:
                    mismatches.append(field)
            
            if not mismatches:
                print(f"âœ“ All fields match - PARITY CONFIRMED")
                results.append({
                    "scenario": scenario['name'],
                    "status": "PASS",
                    "data": admin_data
                })
            else:
                print(f"âœ— Mismatches found: {', '.join(mismatches)}")
                results.append({
                    "scenario": scenario['name'],
                    "status": "FAIL",
                    "reason": f"Parity mismatch: {', '.join(mismatches)}"
                })
        
        except requests.exceptions.Timeout:
            print(f"âœ— Request timeout")
            results.append({
                "scenario": scenario['name'],
                "status": "FAIL",
                "reason": "Request timeout"
            })
        
        except Exception as e:
            print(f"âœ— Error: {e}")
            results.append({
                "scenario": scenario['name'],
                "status": "FAIL",
                "reason": str(e)
            })
        
        time.sleep(1)  # Rate limit between tests
    
    # Summary
    print("\n" + "=" * 60)
    print("PARITY TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for r in results if r['status'] == 'PASS')
    failed = sum(1 for r in results if r['status'] == 'FAIL')
    
    print(f"\nResults: {passed} PASSED, {failed} FAILED out of {len(results)} tests")
    print()
    
    for idx, result in enumerate(results, 1):
        status_symbol = "âœ“" if result['status'] == "PASS" else "âœ—"
        print(f"{status_symbol} [{idx}] {result['scenario']}: {result['status']}")
        if result['status'] == "FAIL" and 'reason' in result:
            print(f"    Reason: {result['reason']}")
    
    print()
    
    if failed == 0:
        print("=" * 60)
        print("âœ“ ALL TESTS PASSED - QUOTE PARITY CONFIRMED")
        print("Ready for Phase 2 (Agent Orchestration)")
        print("=" * 60)
        return True
    else:
        print("=" * 60)
        print(f"âœ— {failed} TEST(S) FAILED - PARITY NOT CONFIRMED")
        print("Debug required before proceeding")
        print("=" * 60)
        return False

if __name__ == "__main__":
    success = test_parity()
    exit(0 if success else 1)

