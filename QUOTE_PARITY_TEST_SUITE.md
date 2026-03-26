# TINSUR-AI Quote Parity Test Suite

**Phase:** 1 - Critical Production Validation  
**Date:** 2026-03-25 00:14 GMT  
**Status:** IN PROGRESS  

---

## 🎯 OBJECTIVE

Validate that quote calculations are **100% identical** between:
- **Admin Panel** (`/api/v1/quotes/calculate`)
- **Client Portal** (`/api/v1/portal/quotes/calculate`)

This ensures customers and admins see the same pricing.

---

## 📋 TEST SCENARIOS

### Scenario 1: Standard Auto Insurance Quote

**Admin Request:**
```bash
POST http://127.0.0.1:8000/api/v1/quotes/calculate
Authorization: Bearer {ADMIN_TOKEN}
Content-Type: application/json

{
  "client_id": "client_001",
  "policy_type_id": "auto_premium",
  "coverage_amount": 100000,
  "duration_months": 12,
  "risk_factors": {
    "age": 35,
    "driving_record": "clean",
    "vehicle_type": "sedan",
    "annual_miles": 15000,
    "location": "urban"
  }
}
```

**Client Portal Request:**
```bash
POST http://127.0.0.1:8000/api/v1/portal/quotes/calculate
Authorization: Bearer {CLIENT_TOKEN}
Content-Type: application/json

{
  "policy_type_id": "auto_premium",
  "coverage_amount": 100000,
  "duration_months": 12,
  "risk_factors": {
    "age": 35,
    "driving_record": "clean",
    "vehicle_type": "sedan",
    "annual_miles": 15000,
    "location": "urban"
  }
}
```

**Expected Result:** ✅ IDENTICAL QUOTES
```json
{
  "base_premium": 1200.00,
  "risk_adjustments": {
    "age": 0.00,
    "driving_record": -50.00,
    "vehicle": 100.00
  },
  "subtotal": 1250.00,
  "taxes": 156.25,
  "admin_fee": 100.00,
  "final_price": 1506.25,
  "validity_days": 30,
  "quote_id": "QUOTE_20260325_001"
}
```

---

### Scenario 2: High-Risk Client

**Parameters:**
```json
{
  "age": 22,
  "driving_record": "accidents",
  "vehicle_type": "sports_car",
  "coverage_amount": 250000,
  "duration_months": 6
}
```

**Expected:** Both endpoints return identical higher premium

---

### Scenario 3: Low-Risk Client

**Parameters:**
```json
{
  "age": 55,
  "driving_record": "clean",
  "vehicle_type": "suv",
  "coverage_amount": 50000,
  "duration_months": 24
}
```

**Expected:** Both endpoints return identical lower premium

---

### Scenario 4: Edge Case - Minimum Coverage

**Parameters:**
```json
{
  "coverage_amount": 10000,
  "duration_months": 1
}
```

**Expected:** Both handle minimum limits correctly

---

### Scenario 5: Edge Case - Maximum Coverage

**Parameters:**
```json
{
  "coverage_amount": 1000000,
  "duration_months": 36
}
```

**Expected:** Both handle maximum limits correctly

---

## 🔍 VALIDATION MATRIX

For each test scenario, verify:

| Field | Admin Value | Client Value | Match? |
|-------|-------------|--------------|--------|
| `base_premium` | ? | ? | ✓ or ✗ |
| `risk_adjustments` | ? | ? | ✓ or ✗ |
| `subtotal` | ? | ? | ✓ or ✗ |
| `taxes` | ? | ? | ✓ or ✗ |
| `admin_fee` | ? | ? | ✓ or ✗ |
| `final_price` | ? | ? | ✓ or ✗ |
| `validity_days` | ? | ? | ✓ or ✗ |

---

## 📊 ACCEPTANCE CRITERIA

### ✅ PASS CONDITIONS
- [ ] All 5 scenarios tested
- [ ] All fields match between admin and client
- [ ] Calculations are mathematically correct
- [ ] Risk factors applied identically
- [ ] Taxes calculated the same way
- [ ] Admin fees not visible to client (optional)

### ❌ FAIL CONDITIONS
- [ ] Any price difference between admin and client
- [ ] Any field mismatch
- [ ] Calculation errors
- [ ] Different risk adjustments applied
- [ ] Inconsistent tax calculation

---

## 🧪 TEST SCRIPT (Python)

```python
import requests
import json
from decimal import Decimal

BASE_URL = "http://127.0.0.1:8000"

# Authentication tokens (placeholder)
ADMIN_TOKEN = "admin_token_here"
CLIENT_TOKEN = "client_token_here"

# Test scenarios
scenarios = [
    {
        "name": "Standard Auto Insurance",
        "params": {
            "policy_type_id": "auto_premium",
            "coverage_amount": 100000,
            "duration_months": 12,
            "risk_factors": {
                "age": 35,
                "driving_record": "clean",
                "vehicle_type": "sedan"
            }
        }
    },
    {
        "name": "High-Risk Client",
        "params": {
            "policy_type_id": "auto_premium",
            "coverage_amount": 250000,
            "duration_months": 6,
            "risk_factors": {
                "age": 22,
                "driving_record": "accidents",
                "vehicle_type": "sports_car"
            }
        }
    },
    # Add more scenarios...
]

def test_parity():
    """Test quote parity between admin and client endpoints"""
    
    results = []
    
    for scenario in scenarios:
        print(f"\nTesting: {scenario['name']}")
        print("-" * 50)
        
        # Admin endpoint
        admin_response = requests.post(
            f"{BASE_URL}/api/v1/quotes/calculate",
            headers={"Authorization": f"Bearer {ADMIN_TOKEN}"},
            json={
                "client_id": "test_client",
                **scenario['params']
            }
        )
        
        # Client endpoint
        client_response = requests.post(
            f"{BASE_URL}/api/v1/portal/quotes/calculate",
            headers={"Authorization": f"Bearer {CLIENT_TOKEN}"},
            json=scenario['params']
        )
        
        if admin_response.status_code != 200:
            print(f"  ERROR: Admin endpoint returned {admin_response.status_code}")
            results.append({"scenario": scenario['name'], "status": "FAIL", "error": "Admin endpoint failed"})
            continue
        
        if client_response.status_code != 200:
            print(f"  ERROR: Client endpoint returned {client_response.status_code}")
            results.append({"scenario": scenario['name'], "status": "FAIL", "error": "Client endpoint failed"})
            continue
        
        admin_data = admin_response.json()
        client_data = client_response.json()
        
        # Compare critical fields
        critical_fields = ["base_premium", "subtotal", "taxes", "final_price"]
        all_match = True
        
        for field in critical_fields:
            admin_val = admin_data.get(field)
            client_val = client_data.get(field)
            
            # Handle floating point comparison
            if isinstance(admin_val, (int, float)) and isinstance(client_val, (int, float)):
                match = abs(Decimal(str(admin_val)) - Decimal(str(client_val))) < Decimal("0.01")
            else:
                match = admin_val == client_val
            
            if not match:
                all_match = False
                print(f"  ✗ {field}: admin={admin_val}, client={client_val}")
            else:
                print(f"  ✓ {field}: {admin_val}")
        
        status = "PASS" if all_match else "FAIL"
        results.append({"scenario": scenario['name'], "status": status})
    
    # Summary
    print("\n" + "=" * 50)
    print("PARITY TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for r in results if r['status'] == 'PASS')
    failed = sum(1 for r in results if r['status'] == 'FAIL')
    
    print(f"Passed: {passed}/{len(results)}")
    print(f"Failed: {failed}/{len(results)}")
    
    for result in results:
        status_symbol = "✓" if result['status'] == "PASS" else "✗"
        print(f"{status_symbol} {result['scenario']}: {result['status']}")
    
    return failed == 0

if __name__ == "__main__":
    success = test_parity()
    exit(0 if success else 1)
```

---

## 🚀 EXECUTION PLAN

### Step 1: Ensure Backend is Running (5 min)
```powershell
# Backend should be running on http://127.0.0.1:8000
# Verify: http://127.0.0.1:8000/docs
```

### Step 2: Get Authentication Tokens (5 min)
```bash
# Get admin token
curl -X POST http://127.0.0.1:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"admin123"}'

# Get client token
curl -X POST http://127.0.0.1:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"client@example.com","password":"client123"}'
```

### Step 3: Run Test Script (10 min)
```bash
cd C:\THUNDERFAM APPS\tinsur-ai
python test_quote_parity.py
```

### Step 4: Document Results (5 min)
- Record all test results
- Note any discrepancies
- Identify root causes if parity fails

---

## 📝 EXPECTED OUTCOME

### If PASS ✅
- Quote parity confirmed 100%
- Proceed to Phase 2 (Agent Orchestration)
- Full confidence in production deployment

### If FAIL ❌
- Identify which fields don't match
- Debug calculation logic
- Fix parity issues
- Re-test until PASS

---

## 🎯 SUCCESS CRITERIA

```
All 5 test scenarios PASS
+ All 7 fields match between admin and client
+ Calculations are mathematically correct
+ No discrepancies found
= READY FOR PHASE 2
```

---

**Status:** READY TO EXECUTE  
**Prerequisite:** Backend running on 127.0.0.1:8000  
**Estimated Time:** 30 minutes  
**Success Rate Target:** 100% parity
