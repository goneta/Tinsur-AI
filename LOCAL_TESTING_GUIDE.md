# LOCAL TESTING GUIDE - SWAGGER UI

**Date:** 2026-03-26 00:10 GMT  
**Purpose:** Step-by-step guide for testing Tinsur-AI locally using Swagger UI  
**Difficulty:** Beginner-Friendly  

---

## 🚀 QUICK START (2 Minutes)

### Step 1: Open Swagger UI
1. **Open your browser**
2. **Go to:** http://127.0.0.1:8000/docs
3. **You'll see:** All 229 API endpoints listed

### Step 2: Browse Endpoints
- Scroll through the list
- Each endpoint shows:
  - HTTP method (GET, POST, etc.)
  - Endpoint path
  - Short description
  - Parameters and request body schema

### Step 3: Test a Public Endpoint (No Auth Needed)
- Find: `GET /` (Root endpoint)
- Click on it (turns blue)
- Click "Try it out" button
- Click "Execute"
- See the response: `{"name": "Tinsur.AI", "version": "1.0.0", "status": "running"}`

---

## 🔐 AUTHENTICATION IN SWAGGER UI

### Method 1: Using Login Endpoint (Recommended)

**Step 1: Find Login Endpoint**
- Scroll to find `/api/v1/auth/login`
- Click to expand

**Step 2: Prepare Login Request**
```json
{
  "email": "admin@example.com",
  "password": "admin123"
}
```

**Step 3: Execute Login**
1. Click "Try it out"
2. Paste the JSON above in the request body
3. Click "Execute"
4. **Copy the token from response** (look for `access_token` field)

**Step 4: Authorize Swagger**
1. Scroll to top
2. Click blue "Authorize" button
3. Paste the token (just the token value, no "Bearer" prefix)
4. Click "Authorize"
5. Click "Close"

### Method 2: Quick Test Without Auth

Some endpoints don't require authentication:
- GET `/` (root)
- GET `/health`
- GET `/docs` (Swagger itself)
- GET `/openapi.json` (API schema)

Try these first without logging in!

---

## 🧪 ENDPOINTS TO TEST

### Group 1: Health & Status (No Auth)

#### Test 1: Root Endpoint
```
GET /
Parameters: None
Expected: {"name": "Tinsur.AI", "version": "1.0.0", "status": "running"}
```

**How to test:**
1. Find `GET /`
2. Click "Try it out"
3. Click "Execute"
4. See response below

#### Test 2: API Health
```
GET /health
Parameters: None
Expected: {"status": "healthy"}
```

---

### Group 2: Authentication

#### Test 3: Login (Admin)
```
POST /api/v1/auth/login
Body: {
  "email": "admin@example.com",
  "password": "admin123"
}
Expected: {
  "access_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

**How to test:**
1. Find `POST /api/v1/auth/login`
2. Click "Try it out"
3. In the request body, paste:
```json
{
  "email": "admin@example.com",
  "password": "admin123"
}
```
4. Click "Execute"
5. **Copy the access_token from response**
6. Use it to authorize other endpoints

#### Test 4: Login (Client)
```
POST /api/v1/auth/login
Body: {
  "email": "client@example.com",
  "password": "client123"
}
Expected: {
  "access_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

---

### Group 3: Quotes (Requires Auth)

#### Test 5: Calculate Quote
```
POST /api/v1/quotes/calculate
Authorization: Bearer $TOKEN
Body: {
  "policy_type_id": "auto_premium",
  "coverage_amount": 100000,
  "duration_months": 12,
  "risk_factors": {
    "age": 35,
    "driving_record": "clean",
    "vehicle_type": "sedan"
  }
}
Expected: {
  "base_premium": 1200,
  "adjustments": [...],
  "subtotal": 1200,
  "taxes": 120,
  "final_price": 1320,
  "validity_days": 30
}
```

**How to test:**
1. Get access token (Test 3 above)
2. Click "Authorize" button
3. Paste token
4. Find `POST /api/v1/quotes/calculate`
5. Click "Try it out"
6. Paste request body (JSON above)
7. Click "Execute"
8. See quote calculation result!

#### Test 6: Get Quote History
```
GET /api/v1/quotes
Authorization: Bearer $TOKEN
Expected: List of quotes for authenticated user
```

---

### Group 4: Agents (AI Features)

#### Test 7: Quote Agent
```
POST /api/v1/agents/quote
Authorization: Bearer $TOKEN
Body: {
  "query": "Calculate premium for a 35-year-old driver with clean record, sedan",
  "context": {
    "age": 35,
    "driving_record": "clean",
    "vehicle_type": "sedan"
  }
}
Expected: AI-generated quote recommendation
```

#### Test 8: Policy Agent
```
POST /api/v1/agents/policy
Authorization: Bearer $TOKEN
Body: {
  "query": "Is this customer eligible for premium coverage?",
  "context": {
    "age": 35,
    "driving_record": "clean"
  }
}
Expected: Eligibility assessment
```

---

## 📝 STEP-BY-STEP TEST WALKTHROUGH

### Complete Testing Scenario (15 minutes)

**Step 1: Check API is Running (2 min)**
```
1. Open: http://127.0.0.1:8000/docs
2. Find: GET /
3. Click "Try it out"
4. Click "Execute"
5. See: {"name": "Tinsur.AI", ...}
✓ API is running!
```

**Step 2: Login as Admin (3 min)**
```
1. Find: POST /api/v1/auth/login
2. Click "Try it out"
3. Paste in Request body:
   {
     "email": "admin@example.com",
     "password": "admin123"
   }
4. Click "Execute"
5. Copy: access_token value from response
6. Click "Authorize" button
7. Paste token (just the token, no "Bearer")
8. Click "Authorize"
✓ You're authenticated!
```

**Step 3: Calculate a Quote (5 min)**
```
1. Find: POST /api/v1/quotes/calculate
2. Click "Try it out"
3. Paste in Request body:
   {
     "policy_type_id": "auto_premium",
     "coverage_amount": 100000,
     "duration_months": 12,
     "risk_factors": {
       "age": 35,
       "driving_record": "clean",
       "vehicle_type": "sedan"
     }
   }
4. Click "Execute"
5. See: Quote calculation with price breakdown
✓ Quote engine works!
```

**Step 4: Test Different Scenarios (5 min)**
```
Try these different profiles:

Scenario A: High-Risk Driver
- age: 22
- driving_record: "accidents"
- vehicle_type: "sports_car"
- See higher premium

Scenario B: Low-Risk Driver
- age: 55
- driving_record: "clean"
- vehicle_type: "suv"
- See lower premium

Scenario C: Different Coverage
- coverage_amount: 50000
- See lower total
```

---

## 🔍 EXPECTED RESPONSES

### Successful Quote Response
```json
{
  "quote_id": "quote_123abc",
  "client_id": "client_001",
  "policy_type": "auto_premium",
  "base_premium": 1200.00,
  "adjustments": [
    {
      "factor": "age",
      "description": "Driver age 35",
      "value": 0
    },
    {
      "factor": "driving_record",
      "description": "Clean driving record",
      "value": -50
    },
    {
      "factor": "vehicle_type",
      "description": "Sedan",
      "value": 100
    }
  ],
  "subtotal": 1250.00,
  "taxes": 125.00,
  "admin_fee": 0.00,
  "final_price": 1375.00,
  "currency": "USD",
  "validity_days": 30,
  "created_at": "2026-03-26T00:10:00Z",
  "status": "pending"
}
```

### Error Response (401 Unauthorized)
```json
{
  "detail": "Not authenticated"
}
```
**Fix:** Use login endpoint to get token first

### Error Response (422 Validation Error)
```json
{
  "detail": [
    {
      "loc": ["body", "policy_type_id"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```
**Fix:** Include all required fields in request body

---

## 💡 TROUBLESHOOTING

### Problem: "Not authenticated" (401)
**Cause:** No token provided or token expired
**Solution:**
1. Go to `/api/v1/auth/login` endpoint
2. Login with `admin@example.com` / `admin123`
3. Copy the `access_token` from response
4. Click "Authorize" button at top
5. Paste token
6. Try endpoint again

### Problem: "Signature verification failed"
**Cause:** Token was generated incorrectly
**Solution:**
1. Use the login endpoint (`/api/v1/auth/login`) instead
2. This will give you a valid token
3. Then use that token for other endpoints

### Problem: "Connection refused"
**Cause:** Backend is not running
**Solution:**
1. Make sure backend is started:
   ```bash
   cd backend
   python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
   ```
2. Wait 3 seconds for server to start
3. Try Swagger again: http://127.0.0.1:8000/docs

### Problem: Swagger UI won't load
**Cause:** Different issues possible
**Solution:**
1. Check backend is running (see above)
2. Try: http://127.0.0.1:8000/redoc (alternative UI)
3. Try: http://127.0.0.1:8000/openapi.json (raw API schema)
4. Restart browser and try again

---

## 📊 ENDPOINTS SUMMARY

| Group | Endpoint | Method | Auth | Purpose |
|-------|----------|--------|------|---------|
| **Health** | `/` | GET | No | Check API status |
| **Health** | `/health` | GET | No | Health check |
| **Auth** | `/api/v1/auth/login` | POST | No | Get access token |
| **Auth** | `/api/v1/auth/logout` | POST | Yes | Logout user |
| **Quotes** | `/api/v1/quotes/calculate` | POST | Yes | Calculate quote |
| **Quotes** | `/api/v1/quotes` | GET | Yes | List quotes |
| **Quotes** | `/api/v1/quotes/{id}` | GET | Yes | Get quote details |
| **Agents** | `/api/v1/agents/quote` | POST | Yes | Quote agent |
| **Agents** | `/api/v1/agents/policy` | POST | Yes | Policy agent |

**Total: 229 endpoints available!**

---

## 🎯 QUICK REFERENCE

### Login Command (Copy-Paste Ready)
```json
{
  "email": "admin@example.com",
  "password": "admin123"
}
```

### Sample Quote Request (Copy-Paste Ready)
```json
{
  "policy_type_id": "auto_premium",
  "coverage_amount": 100000,
  "duration_months": 12,
  "risk_factors": {
    "age": 35,
    "driving_record": "clean",
    "vehicle_type": "sedan"
  }
}
```

### Sample Agent Query (Copy-Paste Ready)
```json
{
  "query": "Calculate premium for 35-year-old clean driver with sedan",
  "context": {
    "age": 35,
    "driving_record": "clean",
    "vehicle_type": "sedan"
  }
}
```

---

## 📞 QUICK ACCESS LINKS

**Swagger UI (Interactive Testing):**
http://127.0.0.1:8000/docs

**ReDoc (Alternative Docs):**
http://127.0.0.1:8000/redoc

**OpenAPI JSON Schema:**
http://127.0.0.1:8000/openapi.json

**API Root:**
http://127.0.0.1:8000/

---

## ✅ TESTING CHECKLIST

- [ ] Open Swagger UI: http://127.0.0.1:8000/docs
- [ ] Test root endpoint (GET /)
- [ ] Login as admin (POST /auth/login)
- [ ] Copy access token
- [ ] Click Authorize button
- [ ] Paste token
- [ ] Test quote endpoint (POST /quotes/calculate)
- [ ] See quote calculation response
- [ ] Try different scenarios
- [ ] Test agent endpoints
- [ ] Verify all responses are correct

---

**Status:** READY TO TEST LOCALLY  
**Next:** Open http://127.0.0.1:8000/docs in your browser!
