# PHASE 2: Agent Orchestration Testing

**Phase:** 2 - AI Agents Production Validation  
**Date:** 2026-03-25 00:20 GMT  
**Status:** IN PROGRESS  

---

## 🎯 OBJECTIVE

Validate that Tinsur-AI AI agents (powered by Google Gemini) are:
1. ✅ Loaded and accessible
2. ✅ Responding to requests
3. ✅ Orchestrating correctly (multi-agent)
4. ✅ Calling backend tools/APIs
5. ✅ Handling errors with fallback paths

---

## 📋 AGENTS TO TEST

### 1. Quote Agent (`a2a_quote_agent`)
**Purpose:** Process quote requests and generate recommendations

**Test Scenario:**
```
Input: "Calculate quote for 35-year-old clean driver, sedan, $100k coverage"
Expected: Returns calculated premium with personalized recommendations
```

### 2. Policy Agent (`a2a_policy_agent`)
**Purpose:** Evaluate policy eligibility and risk assessment

**Test Scenario:**
```
Input: "Is client eligible for premium coverage?"
Expected: Returns eligibility status with risk assessment
```

### 3. Multi-Agent System
**Purpose:** Coordinate between Quote Agent and Policy Agent

**Test Scenario:**
```
Input: "Create quote for customer - evaluate eligibility first"
Expected: Policy Agent evaluates → Quote Agent processes → Combined response
```

### 4. Tool Calls
**Purpose:** Verify agents can call backend APIs

**Test Scenario:**
```
Agent receives request → Calls /api/v1/quotes/calculate → Returns result
```

### 5. Error Fallback Paths
**Purpose:** Ensure graceful degradation on API failures

**Test Scenario:**
```
Backend returns error → Agent catches exception → Returns fallback response
```

---

## 🧪 TEST SUITE

### Test 1: Agent Availability
```bash
Check if agents are loaded in the system
Verify agent names and IDs
Confirm agent endpoints exist
```

### Test 2: Quote Agent Response
```bash
POST /api/v1/agents/quote
{
  "query": "Calculate premium for 35-year-old clean driver, sedan, $100k",
  "context": {
    "client_id": "test_client",
    "policy_type": "auto"
  }
}

Expected Response:
{
  "agent": "quote_agent",
  "response": "Based on the profile...",
  "calculated_premium": 1250.00,
  "recommendations": [...]
}
```

### Test 3: Policy Agent Response
```bash
POST /api/v1/agents/policy
{
  "query": "Evaluate eligibility for premium coverage",
  "context": {
    "client_id": "test_client",
    "age": 35,
    "driving_record": "clean"
  }
}

Expected Response:
{
  "agent": "policy_agent",
  "eligible": true,
  "risk_score": 2,
  "recommendations": [...]
}
```

### Test 4: Multi-Agent Orchestration
```bash
POST /api/v1/agents/orchestrate
{
  "query": "Create complete quote with eligibility check",
  "context": {
    "client_id": "test_client",
    "age": 35,
    "driving_record": "clean",
    "coverage_amount": 100000
  }
}

Expected Response:
{
  "workflow": "eligibility_check -> quote_calculation",
  "eligibility_result": {...},
  "quote_result": {...}
}
```

### Test 5: Tool Call Verification
```bash
Monitor agent request/response logs
Verify API calls are made:
  - /api/v1/quotes/calculate
  - /api/v1/policies/evaluate
  - /api/v1/users/risk-score
Confirm data flows correctly
```

### Test 6: Error Handling
```bash
Send malformed request to agent
Expected: Agent catches error, returns helpful error message
Verify fallback logic works
Check error logging
```

---

## 📊 SUCCESS CRITERIA

### ✅ PASS REQUIREMENTS

- [ ] All 3 agents are accessible
- [ ] Quote Agent returns structured response
- [ ] Policy Agent evaluates correctly
- [ ] Multi-Agent orchestration works
- [ ] Tool calls execute successfully
- [ ] Error handling is graceful
- [ ] Response times < 5 seconds
- [ ] No unhandled exceptions

### ❌ FAIL TRIGGERS

- [ ] Agent endpoint returns 404
- [ ] Agent times out
- [ ] Agent returns error without fallback
- [ ] Tool calls fail silently
- [ ] Inconsistent response format
- [ ] Agent doesn't handle edge cases

---

## 🚀 EXECUTION PLAN

### Step 1: Verify Agent Endpoints (5 min)
- Check if agent endpoints are defined in OpenAPI schema
- Verify endpoint paths and HTTP methods

### Step 2: Test Individual Agents (20 min)
- Test Quote Agent with sample input
- Test Policy Agent with sample input
- Test Tool Calls endpoint

### Step 3: Test Multi-Agent Orchestration (15 min)
- Submit complex request requiring multiple agents
- Verify workflow execution
- Check data flow between agents

### Step 4: Error & Fallback Testing (10 min)
- Send malformed requests
- Test error responses
- Verify fallback paths

### Step 5: Performance Profiling (5 min)
- Measure response times
- Check for bottlenecks
- Log performance metrics

---

## 🎯 EXPECTED AGENT RESPONSES

### Quote Agent Example Response
```json
{
  "agent": "a2a_quote_agent",
  "status": "success",
  "response": "Based on the customer profile (age 35, clean record, sedan), I calculate a premium of $1,250 annually. This includes...",
  "calculated_premium": 1250.00,
  "base_rate": 1200.00,
  "adjustments": [
    {"factor": "age", "value": 0},
    {"factor": "driving_record", "value": -50},
    {"factor": "vehicle_type", "value": 100}
  ],
  "recommendations": [
    "Customer qualifies for Safe Driver Discount",
    "Consider adding comprehensive coverage for additional $150/year"
  ],
  "confidence_score": 0.95,
  "thinking_steps": [
    "Parsed customer profile",
    "Applied risk models",
    "Calculated premium",
    "Generated recommendations"
  ]
}
```

### Policy Agent Example Response
```json
{
  "agent": "a2a_policy_agent",
  "status": "success",
  "response": "Customer is eligible for premium coverage with a low-risk score of 2/10",
  "eligible": true,
  "policy_tier": "premium",
  "risk_score": 2,
  "risk_factors": [
    "Young age (35) - standard risk",
    "Clean driving record - favorable",
    "Vehicle type: sedan - standard risk"
  ],
  "recommendations": [
    "Approve premium tier coverage",
    "Offer extended warranty",
    "No additional underwriting needed"
  ],
  "confidence_score": 0.98
}
```

---

## 📝 TESTING NOTES

- Agents may use Google Gemini API (requires valid API key in .env)
- If API key is invalid, expect API errors
- Agents should handle Gemini rate limits gracefully
- Response may be slightly different based on prompt engineering

---

## ⏰ TIMELINE

- **Expected duration:** 45-60 minutes total
- **Per test:** 8-12 minutes
- **Contingency:** +15 minutes for debugging

---

**Next Step:** Execute agent tests  
**Dependencies:** Backend running, Gemini API key configured  
**Success Target:** All 6 tests PASS
