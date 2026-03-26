#!/usr/bin/env python3
"""
Test Quote Parity between Admin Panel and Client Portal
Validates that both endpoints produce identical calculations
"""

import requests
import json
from decimal import Decimal

BASE_URL = "http://localhost:8000/api/v1"
ADMIN_TOKEN = "test-admin-token"
CLIENT_TOKEN = "test-client-token"

def test_quote_parity():
    """Test that admin and client create quotes identically"""
    
    print("=" * 80)
    print("TINSUR-AI QUOTE PARITY TEST")
    print("=" * 80)
    print()
    
    # Test data
    test_data = {
        "policy_type_id": "550e8400-e29b-41d4-a716-446655440000",  # UUID example
        "coverage_amount": 50000,
        "risk_factors": {
            "age": 35,
            "accidents": 0,
            "vehicle_type": "sedan",
            "annual_mileage": 12000,
            "years_driving": 10
        },
        "duration_months": 12,
        "selected_services": [],
        "financial_overrides": {}
    }
    
    print("TEST DATA:")
    print(json.dumps(test_data, indent=2, default=str))
    print()
    
    # Test 1: Admin Quote Calculation
    print("-" * 80)
    print("TEST 1: ADMIN QUOTE CALCULATION")
    print("-" * 80)
    
    calc_url = f"{BASE_URL}/quotes/calculate"
    headers = {
        "Authorization": f"Bearer {ADMIN_TOKEN}",
        "Content-Type": "application/json"
    }
    
    calc_data = {
        **test_data,
        "client_id": "550e8400-e29b-41d4-a716-446655440001"
    }
    
    try:
        response = requests.post(calc_url, json=calc_data, headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code in [200, 400]:  # 200 = OK, 400 = validation error (still info)
            admin_result = response.json()
            print("Admin Calculation Result:")
            print(json.dumps(admin_result, indent=2, default=str))
            
            if 'final_premium' in admin_result:
                print(f"\n✅ Admin Final Premium: ${admin_result['final_premium']}")
            
        else:
            print(f"❌ Error: {response.text}")
            admin_result = None
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        admin_result = None
    
    print()
    
    # Test 2: Client Quote Calculation
    print("-" * 80)
    print("TEST 2: CLIENT QUOTE CALCULATION (Portal)")
    print("-" * 80)
    
    client_calc_url = f"{BASE_URL}/portal/quotes/calculate"
    client_headers = {
        "Authorization": f"Bearer {CLIENT_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Client doesn't send client_id - it's auto-assigned
    client_calc_data = test_data
    
    try:
        response = requests.post(client_calc_url, json=client_calc_data, headers=client_headers, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code in [200, 400]:
            client_result = response.json()
            print("Client Calculation Result:")
            print(json.dumps(client_result, indent=2, default=str))
            
            if 'final_premium' in client_result:
                print(f"\n✅ Client Final Premium: ${client_result['final_premium']}")
            
        else:
            print(f"❌ Error: {response.text}")
            client_result = None
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        client_result = None
    
    print()
    
    # PARITY CHECK
    print("=" * 80)
    print("PARITY VALIDATION")
    print("=" * 80)
    
    if admin_result and client_result:
        admin_premium = admin_result.get('final_premium')
        client_premium = client_result.get('final_premium')
        
        if admin_premium and client_premium:
            if admin_premium == client_premium:
                print("✅ PARITY CONFIRMED: Admin and Client premium amounts are IDENTICAL")
                print(f"   Both result in: ${admin_premium}")
            else:
                print(f"❌ PARITY MISMATCH:")
                print(f"   Admin:  ${admin_premium}")
                print(f"   Client: ${client_premium}")
        else:
            print("⚠️  Cannot compare - missing final_premium values")
            
        # Check calculation breakdown
        if 'calculation_breakdown' in admin_result and 'calculation_breakdown' in client_result:
            admin_breakdown = admin_result['calculation_breakdown']
            client_breakdown = client_result['calculation_breakdown']
            
            if admin_breakdown == client_breakdown:
                print("✅ Calculation breakdown is IDENTICAL")
            else:
                print("⚠️  Calculation breakdown differs (may indicate risk factors applied differently)")
    else:
        print("❌ Cannot validate parity - one or both results are missing")
    
    print()
    print("=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    test_quote_parity()
