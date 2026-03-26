# TINSUR-AI Production Test Suite

**Backend Status:** ✅ **RUNNING** on http://0.0.0.0:8000  
**Start Time:** 2026-03-24 00:43 GMT  
**Mode:** Production (no reload)  

---

## 🧪 CRITICAL TESTS TO RUN

### TEST 1: Health & Connectivity
```bash
# Check if backend is responding
curl -X GET http://localhost:8000/docs

# Expected: Swagger UI loads (200 OK)
```

**Status:** ⏳ PENDING

---

### TEST 2: Quote Calculation (Admin)
```bash
POST http://localhost:8000/api/v1/quotes/calculate
Authorization: Bearer {ADMIN_TOKEN}
Content-Type: application/json

{
  "client_id": "test-client-123",
  "policy_type_id": "test-policy-456",
  "coverage_amount": 50000,
  "duration_months": 12,
  "risk_factors": {
    "age": 35,
    "driving_record": "clean",
    "vehicle_type": "sedan"
  }
}
```

**Expected Response:**
```json
{
  "quote_id": "quote-uuid",
  "base_price": 1200,
  "premium_adjustments": {
    "age_adjustment": 50,
    "record_adjustment": 0
  },
  "total_premium": 1250,
  "services": ["roadside_assistance", "legal_support"],
  "admin_fees": 100,
  "tax": 156.25,
  "final_price": 1506.25
}
```

**Status:** ⏳ PENDING

---

### TEST 3: Quote Calculation (Client Portal)
```bash
POST http://localhost:8000/api/v1/portal/quotes/calculate
Authorization: Bearer {CLIENT_TOKEN}
Content-Type: application/json

{
  "policy_type_id": "test-policy-456",
  "coverage_amount": 50000,
  "duration_months": 12,
  "risk_factors": {
    "age": 35,
    "driving_record": "clean",
    "vehicle_type": "sedan"
  }
}
```

**Expected:** IDENTICAL result to TEST 2 (parity!)

**Status:** ⏳ PENDING

---

### TEST 4: Create Quote (Admin)
```bash
POST http://localhost:8000/api/v1/quotes/
Authorization: Bearer {ADMIN_TOKEN}
Content-Type: application/json

{
  "client_id": "test-client-123",
  "policy_type_id": "test-policy-456",
  "coverage_amount": 50000,
  "duration_months": 12,
  "risk_factors": { ... }
}
```

**Expected:**
```json
{
  "quote_id": "quote-uuid",
  "status": "draft",
  "created_at": "2026-03-24T00:43:00Z",
  "final_price": 1506.25
}
```

**Status:** ⏳ PENDING

---

### TEST 5: Get Quote
```bash
GET http://localhost:8000/api/v1/quotes/{quote_id}
Authorization: Bearer {TOKEN}
```

**Expected:** Returns full quote details

**Status:** ⏳ PENDING

---

### TEST 6: Send Quote
```bash
POST http://localhost:8000/api/v1/quotes/{quote_id}/send
Authorization: Bearer {ADMIN_TOKEN}
Content-Type: application/json

{
  "recipient_email": "client@example.com",
  "message": "Your quote is ready"
}
```

**Expected:** Quote sent, status changed to "sent"

**Status:** ⏳ PENDING

---

### TEST 7: Approve Quote
```bash
POST http://localhost:8000/api/v1/quotes/{quote_id}/approve
Authorization: Bearer {ADMIN_TOKEN}
```

**Expected:** Quote approved, status changed to "approved"

**Status:** ⏳ PENDING

---

### TEST 8: AI Agent - Quote Agent
```bash
POST http://localhost:8000/api/v1/agents/quote
Authorization: Bearer {TOKEN}
Content-Type: application/json

{
  "query": "Calculate quote for 35-year-old with clean record, sedan, $50k coverage",
  "context": {
    "client_id": "test-client",
    "policy_type": "auto"
  }
}
```

**Expected:** Agent responds with calculated quote and recommendations

**Status:** ⏳ PENDING

---

### TEST 9: AI Agent - Policy Agent
```bash
POST http://localhost:8000/api/v1/agents/policy
Authorization: Bearer {TOKEN}
Content-Type: application/json

{
  "query": "Is this client eligible for premium policy?",
  "context": {
    "client_id": "test-client",
    "age": 35,
    "driving_record": "clean"
  }
}
```

**Expected:** Agent evaluates and returns eligibility + recommendations

**Status:** ⏳ PENDING

---

### TEST 10: Error Handling
```bash
# Test with missing required fields
POST http://localhost:8000/api/v1/quotes/calculate
Authorization: Bearer {TOKEN}
Content-Type: application/json

{
  "client_id": "test"
  # Missing required fields
}
```

**Expected:**
```json
{
  "error": "Validation error",
  "details": {
    "policy_type_id": "Field required",
    "coverage_amount": "Field required"
  }
}
```

**Status:** ⏳ PENDING

---

## 📊 PARITY VALIDATION MATRIX

| Feature | Admin | Client Portal | Match? |
|---------|-------|-----------------|--------|
| Calculate Premium | ✅ | ⏳ | ❓ |
| Create Quote | ✅ | ⏳ | ❓ |
| Quote Amount | ✅ | ⏳ | ❓ |
| Services Included | ✅ | ⏳ | ❓ |
| Taxes/Fees | ✅ | ⏳ | ❓ |
| Final Price | ✅ | ⏳ | ❓ |

---

## 🚀 IMMEDIATE ACTION ITEMS

### PHASE A: Quick Validation (30 min)
- [ ] Confirm backend health (curl /docs)
- [ ] Test quote calculation
- [ ] Verify quote parity
- [ ] Check error handling

### PHASE B: Agent Testing (45 min)
- [ ] Quote Agent responding
- [ ] Policy Agent functional
- [ ] Tool calls working
- [ ] Fallback errors handled

### PHASE C: Production Hardening (1 hour)
- [ ] Security headers added
- [ ] Rate limiting active
- [ ] Logging complete
- [ ] Error tracking enabled

### PHASE D: Final Verification (30 min)
- [ ] All endpoints tested
- [ ] Parity confirmed
- [ ] Performance acceptable
- [ ] Sign-off ready

---

## ✅ SUCCESS CRITERIA

- ✅ All endpoints responding
- ✅ Quote parity validated
- ✅ Agents working
- ✅ Error handling complete
- ✅ No 500 errors
- ✅ Response time < 1s
- ✅ Logging active
- ✅ Security checks passed

---

**Next Step:** Run TEST 1 (Health check)  
**Backend:** ✅ Running  
**Status:** READY FOR TESTING
