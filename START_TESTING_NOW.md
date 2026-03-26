# START TESTING NOW - QUICK START

**Ready to Test:** YES ✅  
**Backend Status:** RUNNING ✅  
**Database Status:** INITIALIZED ✅  

---

## 🚀 QUICK START (30 SECONDS)

### Step 1: Copy This URL
```
http://127.0.0.1:8000/docs
```

### Step 2: Paste in Browser
- Open your browser (Chrome, Firefox, Safari, Edge)
- Paste the URL above
- Press Enter

### Step 3: You'll See
- Interactive API documentation
- All 229 endpoints listed
- "Try it out" buttons for testing

**Done!** You're now in Swagger UI

---

## 🔐 LOGIN (1 MINUTE)

### Find Login Endpoint
1. In Swagger, scroll down
2. Find section: **auth** or **Authentication**
3. Look for: `POST /api/v1/auth/login`
4. Click it (it will expand)

### Test Login
1. Click blue button: "Try it out"
2. In the box below, paste exactly:
```json
{
  "email": "admin@example.com",
  "password": "admin123"
}
```
3. Click blue "Execute" button
4. **Scroll down** to see the response
5. Look for: `"access_token": "eyJ..."`
6. **Copy the entire token value** (the long string)

### Authorize Swagger
1. Scroll to top of page
2. Click blue "Authorize" button
3. Paste your token (just paste it, don't add anything)
4. Click "Authorize"
5. Click "Close"

**Now you're authenticated!**

---

## 💰 TEST QUOTE CALCULATION (2 MINUTES)

### Find Quote Endpoint
1. Scroll down to find: `POST /api/v1/quotes/calculate`
2. Click it to expand

### Test Quote
1. Click "Try it out"
2. In the request body box, paste:
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
3. Click "Execute"
4. **Scroll down** to see response
5. You'll see: base_premium, adjustments, taxes, final_price

**You just calculated a quote!**

---

## 🧪 TRY DIFFERENT SCENARIOS

### Scenario 1: Young Risky Driver
```json
{
  "policy_type_id": "auto_premium",
  "coverage_amount": 250000,
  "duration_months": 6,
  "risk_factors": {
    "age": 22,
    "driving_record": "accidents",
    "vehicle_type": "sports_car"
  }
}
```
→ **Notice: Higher premium!**

### Scenario 2: Older Safe Driver
```json
{
  "policy_type_id": "auto_premium",
  "coverage_amount": 50000,
  "duration_months": 24,
  "risk_factors": {
    "age": 55,
    "driving_record": "clean",
    "vehicle_type": "suv"
  }
}
```
→ **Notice: Lower premium!**

### Scenario 3: Different Coverage
```json
{
  "policy_type_id": "auto_premium",
  "coverage_amount": 500000,
  "duration_months": 12,
  "risk_factors": {
    "age": 40,
    "driving_record": "clean",
    "vehicle_type": "sedan"
  }
}
```
→ **Notice: Different total price!**

---

## 📊 WHAT YOU'LL SEE

### Successful Response
```json
{
  "quote_id": "quote_abc123",
  "base_premium": 1200.0,
  "adjustments": [
    {"factor": "driving_record", "value": -50},
    {"factor": "vehicle_type", "value": 100}
  ],
  "subtotal": 1250.0,
  "taxes": 125.0,
  "final_price": 1375.0,
  "validity_days": 30,
  "status": "pending"
}
```

### This Shows:
- ✅ Quote was calculated
- ✅ Risk adjustments applied
- ✅ Taxes calculated
- ✅ Final price ready
- ✅ Quote valid for 30 days

---

## 🤖 TEST AI AGENTS (Optional)

### Find Agent Endpoints
1. Look for endpoints with "agent" in the name
2. Examples: `/api/v1/agents/quote` or `/api/v1/agents/policy`

### Test Quote Agent
1. Click "Try it out"
2. Paste:
```json
{
  "query": "What premium should I charge for a 35-year-old driver with clean record in a sedan?",
  "context": {
    "age": 35,
    "driving_record": "clean",
    "vehicle_type": "sedan"
  }
}
```
3. Click "Execute"
4. See AI-generated recommendation

---

## ⚠️ IF SOMETHING GOES WRONG

### Problem: "Not authenticated" (401)
**Solution:**
1. Go back to login endpoint
2. Login again (Steps above)
3. Copy new token
4. Click Authorize again
5. Paste new token

### Problem: "Signature verification failed"
**Solution:**
1. This happens if token is invalid
2. Just login again using `/api/v1/auth/login`
3. Use the new token

### Problem: Can't see Swagger
**Solution:**
1. Make sure URL is: http://127.0.0.1:8000/docs (with /docs)
2. Try alternative: http://127.0.0.1:8000/redoc
3. Try API root: http://127.0.0.1:8000/

### Problem: "Connection refused"
**Solution:**
1. Backend may have stopped
2. Restart it (see section below)

---

## 🔄 IF BACKEND STOPS

### To Restart Backend

**Open PowerShell/Terminal and run:**
```bash
cd C:\THUNDERFAM APPS\tinsur-ai\backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

**Then:**
1. Wait 3-5 seconds
2. Try Swagger again: http://127.0.0.1:8000/docs

---

## 📝 CREDENTIALS TO USE

### Admin Account
```
Email:    admin@example.com
Password: admin123
```

### Client Account (if needed)
```
Email:    client@example.com
Password: client123
```

---

## 🎯 ENDPOINTS YOU CAN TEST

| Endpoint | Purpose | Auth? |
|----------|---------|-------|
| `GET /` | Check API status | No |
| `POST /api/v1/auth/login` | Get access token | No |
| `POST /api/v1/quotes/calculate` | Calculate quote | Yes |
| `GET /api/v1/quotes` | List all quotes | Yes |
| `POST /api/v1/agents/quote` | Ask quote agent | Yes |
| `POST /api/v1/agents/policy` | Ask policy agent | Yes |

**Total: 229 endpoints available to explore!**

---

## 🔗 QUICK LINKS

**Start Here:** http://127.0.0.1:8000/docs  
**Alternative:** http://127.0.0.1:8000/redoc  
**API Info:** http://127.0.0.1:8000/openapi.json  

---

## ✅ CHECKLIST

- [ ] Open http://127.0.0.1:8000/docs in browser
- [ ] Find `/api/v1/auth/login`
- [ ] Login with: admin@example.com / admin123
- [ ] Copy access token
- [ ] Click "Authorize" button
- [ ] Paste token
- [ ] Find `/api/v1/quotes/calculate`
- [ ] Click "Try it out"
- [ ] Paste quote request (see above)
- [ ] Click "Execute"
- [ ] See quote calculation response!

---

## 🎉 YOU'RE READY!

The backend is running now.

**Go test it:**
```
http://127.0.0.1:8000/docs
```

Enjoy exploring all 229 API endpoints! 🚀
