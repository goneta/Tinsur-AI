# AI Task Planning Template - Phase 2: Core Insurance Operations

> **About This Task:** This phase implements the core insurance business functionality including policy management, quote generation, payment processing, and client self-service portal.

---

## 1. Task Overview

### Task Title
**Title:** Phase 2: Core Insurance Operations - Policy Management, Quotes & Payments

### Goal Statement
**Goal:** Implement comprehensive policy lifecycle management, AI-powered quote generation system, multi-payment gateway integration (Stripe + Mobile Money), premium tracking with automated reminders, basic financial reporting, and a fully functional client self-service portal. This phase transforms the platform into a usable insurance management system.

---

## 2. Project Analysis & Current State

### Technology & Architecture
- **Backend Framework**: Python FastAPI (builds on Phase 1)
- **Frontend Framework**: Next.js 14+ (builds on Phase 1)
- **Language**: TypeScript, Python 3.11+
- **Database**: PostgreSQL (policies), MongoDB (policy documents), Redis (payment sessions)
- **Payment Gateways**: Stripe, Orange Money, MTN Mobile Money, Moov Money, Wave
- **Cron Jobs**: APScheduler for payment reminders
- **PDF Generation**: ReportLab / WeasyPrint

### Current State
Phase 1 completed:
- ✅ Authentication and RBAC working
- ✅ Client management operational
- ✅ Document upload functional
- ✅ Admin dashboard live

Need to build:
- Policy types and templates
- Quote calculation engine
- Policy lifecycle workflows
- Payment processing infrastructure
- Client portal for policy viewing
- Automated payment reminders

---

## 3. Context & Problem Definition

### Problem Statement
Insurance agents need to quickly generate quotes based on client information and risk profiles, convert quotes to policies, manage the policy lifecycle (renewals, cancellations, endorsements), and track premium payments. Clients need a self-service portal to view policies, make payments, and track claims. The system must support multiple insurance types (Vehicle, Property, Life, Health, Business, Travel, Agriculture) and integrate with both international and local payment methods.

### Success Criteria
- [x] 7 policy types configured with templates
- [x] Quote generation working with AI-powered pricing
- [x] Policy creation from accepted quotes
- [x] Payment gateways integrated (Stripe + 4 Mobile Money providers)
- [x] Automated payment reminders sending (7, 3, 1 day before; 1, 3, 7, 14 days overdue)
- [x] Client portal accessible with policy overview
- [x] Renewal workflows operational
- [x] Basic financial reports (revenue, collections, premiums)
- [x] Mobile-responsive payment flow

---

## 4. Technical Requirements

### Functional Requirements

**Quote Generation:**
- Agent can create quote for client by selecting insurance type
- System calculates premium based on:
  - Client risk profile
  - Asset value/coverage amount
  - Policy duration
  - Coverage options selected
  - Historical claims data (basic scoring)
- Agent can adjust quote manually
- System sends quote to client via email/SMS/WhatsApp
- Quote has validity period (30 days default)
- Client can accept quote via link

**Policy Management:**
- System automatically creates policy upon quote acceptance
- Policy assigned unique policy number
- Policy document generated as PDF with QR code
- Agent can create endorsements (mid-term changes)
- Agent can process renewals
- Agent can cancel policies with proper workflows
- System tracks policy status (active, expired, canceled, lapsed)

**Payment Processing:**
- Client can pay via Stripe (card), Mobile Money, or bank transfer
- System generates payment links for each premium installment
- System supports one-time and recurring payments
- System tracks payment status per policy
- Client receives payment confirmation via email/SMS

**Payment Reminders:**
- System sends reminders 7 days, 3 days, 1 day before due date
- System sends overdue notices 1, 3, 7, 14 days after due date
- Reminders sent via email, SMS, WhatsApp, push notification
- Each reminder includes one-click payment link
- System applies late fees automatically after grace period

**Client Portal:**
- Client can login and view all policies
- Client can see payment history and upcoming payments
- Client can make payments through portal
- Client can download policy documents
- Client can request quotes
- Client can view claims status (Phase 3)

### Non-Functional Requirements
- **Payment Security**: PCI DSS compliance, tokenization
- **Quote Generation**: < 3 seconds for standard quotes
- **Payment Processing**: Real-time confirmation
- **Reminder Delivery**: 99% delivery rate
- **Portal Performance**: Fast loading on mobile connections

### Technical Constraints
- Must integrate with existing multi-tenant architecture
- Must maintain data isolation between companies
- Must support XOF currency (West African CFA Franc)
- Must comply with CIMA insurance regulations

---

## 5. Data & Database Changes

### Database Schema Changes

**PostgreSQL Tables:**

```sql
-- Policy types table
CREATE TABLE policy_types (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(id),
    name VARCHAR(100) NOT NULL, -- 'Vehicle', 'Property', 'Life', etc.
    code VARCHAR(50) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Quotes table
CREATE TABLE quotes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(id),
    client_id UUID REFERENCES clients(id),
    policy_type_id UUID REFERENCES policy_types(id),
    quote_number VARCHAR(50) UNIQUE NOT NULL,
    coverage_amount DECIMAL(15, 2),
    premium_amount DECIMAL(15, 2) NOT NULL,
    premium_frequency VARCHAR(50) DEFAULT 'annual', -- 'monthly', 'quarterly', 'annual'
    duration_months INTEGER DEFAULT 12,
    risk_score DECIMAL(5, 2),
    discount_percent DECIMAL(5, 2) DEFAULT 0,
    final_premium DECIMAL(15, 2) NOT NULL,
    details JSONB, -- Additional quote details
    status VARCHAR(50) DEFAULT 'draft', -- 'draft', 'sent', 'accepted', 'rejected', 'expired'
    valid_until DATE,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Policies table
CREATE TABLE policies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(id),
    client_id UUID REFERENCES clients(id),
    policy_type_id UUID REFERENCES policy_types(id),
    quote_id UUID REFERENCES quotes(id),
    policy_number VARCHAR(50) UNIQUE NOT NULL,
    coverage_amount DECIMAL(15, 2),
    premium_amount DECIMAL(15, 2) NOT NULL,
    premium_frequency VARCHAR(50) DEFAULT 'annual',
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    status VARCHAR(50) DEFAULT 'active', -- 'active', 'expired', 'canceled', 'lapsed'
    cancellation_reason TEXT,
    policy_document_url VARCHAR(500),
    qr_code_data TEXT,
    details JSONB,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Premium schedules table
CREATE TABLE premium_schedules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    policy_id UUID REFERENCES policies(id) ON DELETE CASCADE,
    installment_number INTEGER NOT NULL,
    due_date DATE NOT NULL,
    amount DECIMAL(15, 2) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'paid', 'overdue', 'waived'
    paid_amount DECIMAL(15, 2) DEFAULT 0,
    paid_date DATE,
    late_fee DECIMAL(10, 2) DEFAULT 0,
    grace_period_days INTEGER DEFAULT 30,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Payments table
CREATE TABLE payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(id),
    client_id UUID REFERENCES clients(id),
    policy_id UUID REFERENCES policies(id),
    premium_schedule_id UUID REFERENCES premium_schedules(id),
    payment_method VARCHAR(50) NOT NULL, -- 'stripe', 'orange_money', 'mtn_money', etc.
    amount DECIMAL(15, 2) NOT NULL,
    currency VARCHAR(10) DEFAULT 'XOF',
    status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'completed', 'failed', 'refunded'
    transaction_id VARCHAR(255),
    payment_gateway_response JSONB,
    payment_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Payment reminders log
CREATE TABLE payment_reminders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    premium_schedule_id UUID REFERENCES premium_schedules(id),
    reminder_type VARCHAR(50) NOT NULL, -- 'upcoming_7d', 'upcoming_3d', 'upcoming_1d', 'overdue_1d', etc.
    sent_at TIMESTAMP NOT NULL,
    delivery_method VARCHAR(50) NOT NULL, -- 'email', 'sms', 'whatsapp', 'push'
    delivery_status VARCHAR(50) DEFAULT 'sent',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_policies_company_id ON policies(company_id);
CREATE INDEX idx_policies_client_id ON policies(client_id);
CREATE INDEX idx_policies_status ON policies(status);
CREATE INDEX idx_quotes_company_id ON quotes(company_id);
CREATE INDEX idx_quotes_client_id ON quotes(client_id);
CREATE INDEX idx_payments_policy_id ON payments(policy_id);
CREATE INDEX idx_premium_schedules_due_date ON premium_schedules(due_date);
CREATE INDEX idx_premium_schedules_status ON premium_schedules(status);
```

---

## 6. API & Backend Changes

### Server Actions

**Quote Endpoints (`/api/v1/quotes`):**
- `POST /quotes` - Create new quote
- `GET /quotes` - List quotes with filters
- `GET /quotes/{id}` - Get quote details
- `PUT /quotes/{id}` - Update quote
- `POST /quotes/{id}/send` - Send quote to client
- `POST /quotes/{id}/accept` - Accept quote (client or agent)
- `POST /quotes/{id}/reject` - Reject quote
- `POST /quotes/{id}/calculate` - Recalculate premium

**Policy Endpoints (`/api/v1/policies`):**
- `POST /policies` - Create policy (from quote or direct)
- `GET /policies` - List policies with filters
- `GET /policies/{id}` - Get policy details
- `PUT /policies/{id}` - Update policy
- `POST /policies/{id}/renew` - Renew policy
- `POST /policies/{id}/cancel` - Cancel policy
- `POST /policies/{id}/endorse` - Create endorsement
- `GET /policies/{id}/document` - Download policy PDF

**Payment Endpoints (`/api/v1/payments`):**
- `POST /payments/initiate` - Initiate payment
- `POST /payments/webhook/stripe` - Stripe webhook
- `POST /payments/webhook/mobile-money` - Mobile Money webhook
- `GET /payments/{id}` - Get payment status
- `GET /payments/policy/{policy_id}` - Get payments for policy

**Client Portal Endpoints (`/api/v1/portal`):**
- `GET /portal/policies` - Get my policies
- `GET /portal/payments` - Get my payment history
- `POST /portal/pay` - Initiate payment
- `GET /portal/documents` - Get my documents

---

## 7. Frontend Changes

### New Components

**Policy Management:**
- `app/(dashboard)/policies/page.tsx` - Policies list
- `app/(dashboard)/policies/[id]/page.tsx` - Policy details
- `app/(dashboard)/quotes/page.tsx` - Quotes list
- `app/(dashboard)/quotes/new/page.tsx` - Create quote
- `components/policies/policy-table.tsx`
- `components/policies/policy-card.tsx`
- `components/quotes/quote-form.tsx`
- `components/quotes/quote-calculator.tsx`

**Payment Components:**
- `components/payments/payment-method-selector.tsx`
- `components/payments/stripe-payment-form.tsx`
- `components/payments/mobile-money-payment.tsx`
- `components/payments/payment-history-table.tsx`

**Client Portal:**
- `app/(portal)/layout.tsx` - Portal layout
- `app/(portal)/my-policies/page.tsx` - My policies
- `app/(portal)/payments/page.tsx` - Payment history
- `app/(portal)/pay/[id]/page.tsx` - Payment page
- `components/portal/policy-overview-card.tsx`

---

## 8. Implementation Plan

### Week 1-2: Policy & Quote Backend
- [ ] Create policy types seed data
- [ ] Implement quote calculation logic
- [ ] Create quote CRUD endpoints
- [ ] Implement policy creation from quote
- [ ] Create policy CRUD endpoints
- [ ] Implement quote PDF generation
- [ ] Write tests

### Week 3-4: Payment Integration
- [ ] Setup Stripe integration
- [ ] Implement Mobile Money providers
- [ ] Create payment initiation endpoint
- [ ] Implement webhook handlers
- [ ] Create premium schedule automation
- [ ] Test payment flows

### Week 5-6: Payment Reminders
- [ ] Create APScheduler jobs
- [ ] Implement reminder logic
- [ ] Setup email/SMS/WhatsApp providers
- [ ] Create reminder templates
- [ ] Test reminder delivery

### Week 7-8: Policy Management UI
- [ ] Create quote creation form
- [ ] Implement policy list and details pages
- [ ] Create policy document viewer
- [ ] Implement renewal flow UI
- [ ] Test agent workflows

### Week 9-10: Client Portal
- [ ] Create portal layout
- [ ] Implement policy overview
- [ ] Create payment page
- [ ] Integrate payment methods
- [ ] Test client workflows

### Week 11-12: Financial Reporting
- [ ] Create revenue dashboards
- [ ] Implement collection reports
- [ ] Create premium aging reports
- [ ] Add charts and visualizations
- [ ] Test and deploy

---

## 9. Mandatory Rules & Best Practices

Follow ALL rules from Phase 1 plus:

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

### Payment Security
- Never store raw card details
- Use tokenization for all payment methods
- Validate webhooks with signatures
- Log all payment attempts

### Quote Calculation
- Always validate input data
- Apply rate limiting to prevent abuse
- Cache calculation results
- Log all quotes for audit

### Reminder System
- Respect opt-out preferences
- Track delivery status
- Handle failures gracefully
- Don't spam (max 1 reminder per day per type)

---

## 10. Definition of Done

- ✅ All 7 policy types configured
- ✅ Agent can create and send quotes
- ✅ Client can accept quote via email link
- ✅ Policy created automatically from accepted quote
- ✅ Policy PDF generated with QR code
- ✅ Stripe payments working
- ✅ Mobile Money payments working
- ✅ Payment reminders sending automatically
- ✅ Client portal shows policies and payments
- ✅ Client can make payment through portal
- ✅ Financial reports showing revenue and collections
- ✅ All tests passing
- ✅ Deployed to staging

---

**Task Version**: 1.0  
**Estimated Duration**: 12 weeks (3 months)  
**Status**: Ready for Implementation

#### Handle Alembic Duplicate Column (MANDATORY)
**File:** `handle_alembic_duplicate_column.mdc`

**Summary:** Prevent migration failures when a column already exists (e.g., SQLite drift).

**Checklist:**
- [ ] If Alembic upgrade fails with "duplicate column name", inspect the migration.
- [ ] Make the migration idempotent by checking column existence before `op.add_column`.
- [ ] Re-run `alembic upgrade head` after patching.

#### Handle Unicode Decode Errors (MANDATORY)
**File:** `handle_unicode_decode_in_scripts.mdc`

**Summary:** Prevent script crashes when reading files with mixed encodings.

**Checklist:**
- [ ] If a Python script raises `UnicodeDecodeError`, reopen files with `encoding="utf-8", errors="replace"` or use a safer fallback.
- [ ] Avoid failing mid-batch; ensure all files are still processed.

#### Seed Many-to-Many Client-Company (MANDATORY)
**File:** `seed_many_to_many_client_company.mdc`

**Summary:** Client-Company is many-to-many; seeding must use `client.companies.append(company)` rather than `client.company_id`.

**Checklist:**
- [ ] When seeding Clients, do not pass `company_id` to `Client(...)`.
- [ ] Associate companies through `client.companies.append(company)`.

#### Handle Missing Quote Columns (MANDATORY)
**File:** `handle_missing_quote_columns_migration.mdc`

**Summary:** If seed or queries fail due to missing quote snapshot columns, add a minimal migration.

**Checklist:**
- [ ] When SQLite error mentions `quotes.admin_fee_percent` or `quotes.admin_discount_percent`, add a targeted migration.
- [ ] Make migration idempotent (check columns before add).
- [ ] Re-run `alembic upgrade head` then re-run seed.

