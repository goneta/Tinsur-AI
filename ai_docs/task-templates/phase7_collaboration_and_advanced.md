# AI Task Planning Template - Phase 7: Collaboration & Advanced Features

> **About This Task:** This phase implements inter-company collaboration features, advanced AI capabilities (predictive analytics), enhanced fraud detection with ML models, comprehensive ticket/support system, referral and loyalty programs, social media integration, QR code verification, and telematics for usage-based insurance.

---

## 1. Task Overview

### Task Title
**Title:** Phase 7: Collaboration & Advanced Features - Inter-Company & Advanced AI

### Goal Statement
**Goal:** Build sophisticated collaboration features enabling insurance companies to securely share information, implement advanced AI for predictive analytics and churn prevention, enhance fraud detection with machine learning models, create a comprehensive support ticketing system, launch referral and loyalty programs, integrate social media marketing, implement QR code verification for documents, and add telematics support for usage-based insurance.

---

## 2. Success Criteria

- [x] Inter-company document sharing working securely
- [x] Co-insurance workflows operational
- [x] Advanced AI predictive models deployed (churn, claims likelihood)
- [x] ML-based fraud detection flagging high-risk claims
- [x] Ticket system handling support requests
- [x] Referral program tracking conversions
- [x] Loyalty points system operational
- [x] Social media posting scheduled
- [x] QR code verification portal public
- [x] Telematics data integrated for UBI policies
- [x] All features tested and deployed

---

## 3. Database Schema

```sql
-- Inter-company sharing
CREATE TABLE inter_company_shares (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    from_company_id UUID REFERENCES companies(id),
    to_company_id UUID REFERENCES companies(id),
    resource_type VARCHAR(50), -- 'document', 'client_data', 'claim_info'
    resource_id UUID,
    access_level VARCHAR(50) DEFAULT 'read', -- 'read', 'write'
    expires_at TIMESTAMP,
    is_revoked BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Tickets
CREATE TABLE tickets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(id),
    client_id UUID REFERENCES clients(id),
    ticket_number VARCHAR(50) UNIQUE NOT NULL,
    category VARCHAR(100), -- 'technical', 'billing', 'claim', 'complaint'
    priority VARCHAR(50) DEFAULT 'medium', -- 'low', 'medium', 'high', 'urgent'
    status VARCHAR(50) DEFAULT 'open', -- 'open', 'in_progress', 'resolved', 'closed'
    subject VARCHAR(255) NOT NULL,
    description TEXT,
    assigned_to UUID REFERENCES users(id),
    resolved_at TIMESTAMP,
    sla_breach_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Referrals
CREATE TABLE referrals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(id),
    referrer_client_id UUID REFERENCES clients(id),
    referred_client_id UUID REFERENCES clients(id),
    referral_code VARCHAR(50) UNIQUE NOT NULL,
    status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'converted', 'expired'
    reward_amount DECIMAL(10, 2),
    reward_paid BOOLEAN DEFAULT FALSE,
    converted_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Loyalty points
CREATE TABLE loyalty_points (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID REFERENCES clients(id),
    points_earned INTEGER DEFAULT 0,
    points_redeemed INTEGER DEFAULT 0,
    points_balance INTEGER DEFAULT 0,
    tier VARCHAR(50) DEFAULT 'bronze', -- 'bronze', 'silver', 'gold', 'platinum'
    created_at TIMESTAMP DEFAULT NOW()
);

-- Telematics data
CREATE TABLE telematics_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    policy_id UUID REFERENCES policies(id),
    device_id VARCHAR(255) NOT NULL,
    trip_date DATE NOT NULL,
    distance_km DECIMAL(10, 2),
    avg_speed DECIMAL(5, 2),
    max_speed DECIMAL(5, 2),
    harsh_braking_count INTEGER DEFAULT 0,
    harsh_acceleration_count INTEGER DEFAULT 0,
    night_driving_km DECIMAL(10, 2),
    safety_score DECIMAL(5, 2),
    created_at TIMESTAMP DEFAULT NOW()
);

-- ML models metadata
CREATE TABLE ml_models (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    model_name VARCHAR(255) NOT NULL,
    model_type VARCHAR(100), -- 'churn_prediction', 'fraud_detection', 'claim_likelihood'
    model_version VARCHAR(50),
    accuracy DECIMAL(5, 4),
    deployed_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 4. Implementation Plan

### Week 1-4: Inter-Company Features
- [ ] Build company directory/network
- [ ] Implement sharing workflows
- [ ] Create access control system
- [ ] Build co-insurance management
- [ ] Test inter-company collaboration

### Week 5-8: Advanced AI
- [ ] Train churn prediction model
- [ ] Train claims likelihood model
- [ ] Implement predictive analytics API
- [ ] Build dashboards for predictions
- [ ] Deploy ML models to production

### Week 9-12: Enhanced Fraud Detection
- [ ] Collect training data for fraud model
- [ ] Train ML fraud detection model
- [ ] Implement scoring system
- [ ] Create investigation workflows
- [ ] Build fraud analyst dashboard

### Week 13-16: Ticket System
- [ ] Create ticket management backend
- [ ] Implement SLA tracking
- [ ] Build ticket assignment logic
- [ ] Create support agent UI
- [ ] Build client ticket portal
- [ ] Add satisfaction surveys

### Week 17-20: Referral & Loyalty
- [ ] Build referral code generation
- [ ] Implement tracking system
- [ ] Create reward payout logic
- [ ] Build loyalty points engine
- [ ] Create tier progression
- [ ] Build redemption system

### Week 21-24: Social & Advanced
- [ ] Integrate social media APIs
- [ ] Create posting scheduler
- [ ] Build QR verification portal
- [ ] Implement telematics integration
- [ ] Create UBI pricing engine
- [ ] Test and deploy

---

## 5. Advanced AI Models

### Churn Prediction
```python
# Features for churn model
features = [
    'months_since_policy_start',
    'number_of_claims',
    'claim_approval_rate',
    'payment_delay_days',
    'customer_service_interactions',
    'premium_amount',
    'age',
    'number_of_policies'
]

# Output: churn_probability (0-1)
```

### Claims Likelihood
```python
# Features for claims prediction
features = [
    'client_age',
    'vehicle_age',
    'driving_experience_years',
    'previous_claims_count',
    'coverage_amount',
    'occupation_risk_score',
    'geographical_risk_score'
]

# Output: claim_likelihood_next_year (0-1)
```

### Fraud Detection
```python
# Features for fraud detection
features = [
    'claim_amount',
    'time_since_policy_start',
    'claim_frequency',
    'claim_timing_pattern',
    'documentation_completeness',
    'claim_settlement_speed_request',
    'geolocation_anomalies',
    'beneficiary_changes'
]

# Output: fraud_risk_score (0-100)
```

---

## 6. Referral Program Flow

1. Client shares referral code/link
2. New client signs up using code
3. System tracks attribution
4. New client purchases policy (conversion)
5. System calculates reward
6. Reward credited to referrer
7. Notification sent to referrer

---

## 7. QR Code Verification

### Generation
- Encode: Policy number, client name, expiry date, verification URL
- Add to policy PDF
- Digital signature for tamper protection

### Verification Portal
- Public URL: verify.insuranceplatform.com
- Scan QR or enter policy number
- Display: Policy status, coverage summary, validity
- Log all verification attempts

---

## 8. Mandatory Rules & Best Practices

Follow ALL rules from Phase 1 and `ai_task_template_skeleton.md`.

### New Mandatory Rules

#### Analyze Build Failures (MANDATORY)
**File:** `analyze_build_failure.mdc`

**Checklist:**
- [ ] If build fails with exit code 1, capture full logs (`npm run build > log.txt 2>&1`)
- [ ] Read the full log file
- [ ] Run `npx tsc --noEmit` to isolate TypeScript errors

#### Zod Resolver Type Mismatch
**File:** `zod_resolver_type_mismatch.mdc`

**Checklist:**
- [ ] Remove `.default()` from schema for controlled form fields
- [ ] Provide explicit `defaultValues` in `useForm`
- [ ] Verify `z.infer<typeof schema>` matches `useForm<Type>`

---

## 9. Definition of Done

- ✅ Inter-company sharing working
- ✅ Co-insurance management operational
- ✅ Churn prediction model deployed
- ✅ Fraud ML model flagging high-risk claims
- ✅ Ticket system handling requests
- ✅ Referral program tracking conversions
- ✅ Loyalty points system operational
- ✅ Social media integration working
- ✅ QR verification portal live
- ✅ Telematics data integrated for UBI
- ✅ All tests passing
- ✅ Deployed to production

---

**Task Version**: 1.0  
**Estimated Duration**: 24 weeks (~6 months)  
**Status**: Ready for Implementation
