# AI Task Planning Template - Phase 6: Financial Management

> **About This Task:** This phase implements a complete financial accounting system including chart of accounts, general ledger, accounts receivable/payable, bank reconciliation, fixed assets management, comprehensive financial reporting, and integration with external accounting software.

---

## 1. Task Overview

### Task Title
**Title:** Phase 6: Financial Management - Complete Accounting & Financial Reporting

### Goal Statement
**Goal:** Build a robust financial accounting system supporting double-entry bookkeeping, automated journal entries, comprehensive financial reporting (P&L, Balance Sheet, Cash Flow), accounts receivable/payable management, bank reconciliation, fixed assets tracking, compliance reporting (OHADA, CIMA standards), and integration with QuickBooks/Sage. This enables insurance companies to maintain accurate financial records and generate regulatory reports.

---

## 2. Success Criteria

- [x] Chart of accounts configured (OHADA compliant)
- [x] General ledger operational with double-entry bookkeeping
- [x] Automated journal entries from policy/payment transactions
- [x] Accounts receivable tracking premium receivables
- [x] Accounts payable tracking claims payable
- [x] Bank reconciliation automated
- [x] Fixed assets registered and depreciated
- [x] Financial statements generated (P&L, Balance Sheet, Cash Flow)
- [x] Revenue reports (daily, weekly, monthly, quarterly, annual)
- [x] Compliance reports for regulators
- [x] Integration with QuickBooks/Xero working
- [x] All financial dashboards operational

---

## 3. Database Schema

```sql
-- Chart of accounts
CREATE TABLE chart_of_accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(id),
    account_code VARCHAR(50) UNIQUE NOT NULL,
    account_name VARCHAR(255) NOT NULL,
    account_type VARCHAR(50) NOT NULL, -- 'asset', 'liability', 'equity', 'revenue', 'expense'
    account_category VARCHAR(100),
    parent_account_id UUID REFERENCES chart_of_accounts(id),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- General ledger
CREATE TABLE general_ledger (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(id),
    account_id UUID REFERENCES chart_of_accounts(id),
    transaction_date DATE NOT NULL,
    description TEXT,
    debit_amount DECIMAL(15, 2) DEFAULT 0,
    credit_amount DECIMAL(15, 2) DEFAULT 0,
    balance DECIMAL(15, 2),
    reference_type VARCHAR(50), -- 'payment', 'policy', 'claim', 'payroll', etc.
    reference_id UUID,
    posted_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Accounts receivable
CREATE TABLE accounts_receivable (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(id),
    client_id UUID REFERENCES clients(id),
    policy_id UUID REFERENCES policies(id),
    invoice_number VARCHAR(50) UNIQUE NOT NULL,
    invoice_date DATE NOT NULL,
    due_date DATE NOT NULL,
    amount DECIMAL(15, 2) NOT NULL,
    paid_amount DECIMAL(15, 2) DEFAULT 0,
    outstanding_amount DECIMAL(15, 2),
    status VARCHAR(50) DEFAULT 'unpaid', -- 'unpaid', 'partially_paid', 'paid', 'overdue'
    aging_category VARCHAR(50), -- 'current', '30_days', '60_days', '90_days', '120+_days'
    created_at TIMESTAMP DEFAULT NOW()
);

-- Accounts payable
CREATE TABLE accounts_payable (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(id),
    vendor_name VARCHAR(255),
    claim_id UUID REFERENCES claims(id),
    invoice_number VARCHAR(50),
    invoice_date DATE NOT NULL,
    due_date DATE NOT NULL,
    amount DECIMAL(15, 2) NOT NULL,
    paid_amount DECIMAL(15, 2) DEFAULT 0,
    outstanding_amount DECIMAL(15, 2),
    status VARCHAR(50) DEFAULT 'unpaid',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Bank accounts
CREATE TABLE bank_accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(id),
    bank_name VARCHAR(255) NOT NULL,
    account_number VARCHAR(100) NOT NULL,
    account_type VARCHAR(50), -- 'checking', 'savings', 'money_market'
    currency VARCHAR(10) DEFAULT 'XOF',
    current_balance DECIMAL(15, 2),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Bank reconciliations
CREATE TABLE bank_reconciliations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bank_account_id UUID REFERENCES bank_accounts(id),
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    statement_balance DECIMAL(15, 2),
    book_balance DECIMAL(15, 2),
    reconciled_balance DECIMAL(15, 2),
    difference DECIMAL(15, 2),
    status VARCHAR(50) DEFAULT 'draft', -- 'draft', 'completed'
    reconciled_by UUID REFERENCES users(id),
    reconciled_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Fixed assets
CREATE TABLE fixed_assets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(id),
    asset_name VARCHAR(255) NOT NULL,
    asset_type VARCHAR(100), -- 'equipment', 'furniture', 'vehicle', 'building'
    purchase_date DATE NOT NULL,
    purchase_cost DECIMAL(15, 2) NOT NULL,
    depreciation_method VARCHAR(50), -- 'straight_line', 'declining_balance'
    useful_life_years INTEGER,
    salvage_value DECIMAL(15, 2) DEFAULT 0,
    accumulated_depreciation DECIMAL(15, 2) DEFAULT 0,
    book_value DECIMAL(15, 2),
    status VARCHAR(50) DEFAULT 'active', -- 'active', 'disposed', 'fully_depreciated'
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 4. API Endpoints

### Accounting Endpoints
- `POST /api/v1/accounting/journal-entry` - Create journal entry
- `GET /api/v1/accounting/general-ledger` - Get general ledger
- `GET /api/v1/accounting/trial-balance` - Get trial balance
- `POST /api/v1/accounting/period-close` - Close accounting period

### Receivables Endpoints
- `GET /api/v1/receivables` - List receivables
- `GET /api/v1/receivables/aging` - Aging report

### Payables Endpoints
- `GET /api/v1/payables` - List payables
- `POST /api/v1/payables/pay` - Record payment

### Bank Reconciliation
- `POST /api/v1/bank/reconciliation` - Create reconciliation
- `GET /api/v1/bank/reconciliations` - List reconciliations

### Financial Reports
- `GET /api/v1/reports/profit-loss` - P&L Statement
- `GET /api/v1/reports/balance-sheet` - Balance Sheet
- `GET /api/v1/reports/cash-flow` - Cash Flow Statement
- `GET /api/v1/reports/revenue` - Revenue reports

### Fixed Assets
- `POST /api/v1/assets` - Register asset
- `GET /api/v1/assets` - List assets
- `POST /api/v1/assets/{id}/depreciate` - Calculate depreciation

---

## 5. Implementation Plan

### Week 1-3: Chart of Accounts & GL
- [ ] Design chart of accounts (OHADA standard)
- [ ] Create account management
- [ ] Implement general ledger
- [ ] Build double-entry system
- [ ] Create journal entry UI

### Week 4-6: Automated Accounting
- [ ] Implement auto journal entries for policies
- [ ] Auto entries for payments
- [ ] Auto entries for claims
- [ ] Auto entries for payroll
- [ ] Test transaction flows

### Week 7-9: AR & AP
- [ ] Create receivables tracking
- [ ] Implement aging reports
- [ ] Build payables management
- [ ] Create payment workflows
- [ ] Build AR/AP dashboards

### Week 10-12: Bank Reconciliation
- [ ] Implement bank statement import
- [ ] Create matching algorithms
- [ ] Build reconciliation UI
- [ ] Test reconciliation workflow

### Week 13-15: Financial Reporting
- [ ] Build P&L statement generator
- [ ] Create balance sheet generator
- [ ] Implement cash flow statement
- [ ] Create revenue reports
- [ ] Build financial dashboards

### Week 16-18: Fixed Assets & Compliance
- [ ] Create asset registration
- [ ] Implement depreciation calculations
- [ ] Build compliance reports
- [ ] Create audit reports
- [ ] Test regulatory submissions

### Week 19-20: External Integration
- [ ] Build QuickBooks integration
- [ ] Create Xero integration
- [ ] Test data synchronization
- [ ] Final testing and deployment

---

## 6. Key Financial Reports

### Profit & Loss Statement
- Revenue by product line
- Total expenses
- Operating income
- Net income
- Period comparisons

### Balance Sheet
- Assets (current & fixed)
- Liabilities
- Equity
- Financial ratios

### Cash Flow Statement
- Operating activities
- Investing activities
- Financing activities

### Revenue Reports
- Daily revenue summary
- Weekly revenue trends
- Monthly revenue breakdown
- Revenue by channel
- Revenue forecasting

### Compliance Reports
- CIMA regulatory reports
- Solvency margin reports
- Tax reports (VAT, corporate tax)

---

## 7. Mandatory Rules & Best Practices

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

## 8. Definition of Done

- ✅ Chart of accounts configured
- ✅ General ledger operational
- ✅ Automated journal entries working
- ✅ AR aging reports generated
- ✅ AP management functional
- ✅ Bank reconciliation completed
- ✅ Fixed assets tracked and depreciated
- ✅ P&L, Balance Sheet, Cash Flow generated
- ✅ Revenue reports available
- ✅ QuickBooks integration working
- ✅ All tests passing
- ✅ Deployed to staging

---

**Task Version**: 1.0  
**Estimated Duration**: 20 weeks (~5 months)  
**Status**: Ready for Implementation
