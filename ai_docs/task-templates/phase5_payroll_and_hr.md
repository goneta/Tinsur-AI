# AI Task Planning Template - Phase 5: Payroll & HR

> **About This Task:** This phase implements a complete payroll management system supporting employee master data, salary structures, automated payroll processing, time & attendance, leave management, tax calculations (Côte d'Ivoire compliance), payslip generation, and employee self-service.

---

## 1. Task Overview

### Task Title
**Title:** Phase 5: Payroll & HR - Comprehensive Payroll System with CNPS Compliance

### Goal Statement
**Goal:** Build a full-featured payroll system that automates salary calculations, manages allowances and deductions, ensures compliance with Côte d'Ivoire tax regulations and CNPS (Social Security) requirements, generates professional payslips, integrates with time & attendance, manages employee leave, and provides self-service capabilities. This enables insurance companies to manage their workforce payroll efficiently and compliantly.

---

## 2. Success Criteria

- [x] Employee master data management operational
- [x] Salary structure configured (base + allowances)
- [x] Automated payroll run working
- [x] Tax calculations accurate (Côte d'Ivoire brackets)
- [x] CNPS contributions calculated correctly
- [x] Payslips generated and distributed automatically
- [x] Time & attendance integrated
- [x] Leave management functional
- [x] Employee self-service portal working
- [x] Payroll accounting entries automated
- [x] All statutory reports generated

---

## 3. Database Schema

```sql
-- Employees (extends users table)
CREATE TABLE employees (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    company_id UUID REFERENCES companies(id),
    employee_number VARCHAR(50) UNIQUE NOT NULL,
    department VARCHAR(100),
    position VARCHAR(100),
    date_of_hire DATE NOT NULL,
    contract_type VARCHAR(50), -- 'permanent', 'temporary', 'contract'
    bank_name VARCHAR(255),
    bank_account_number VARCHAR(100),
    tax_id VARCHAR(100),
    cnps_number VARCHAR(100),
    emergency_contact JSONB,
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Salary structures
CREATE TABLE salary_structures (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    employee_id UUID REFERENCES employees(id),
    base_salary DECIMAL(15, 2) NOT NULL,
    housing_allowance DECIMAL(15, 2) DEFAULT 0,
    transport_allowance DECIMAL(15, 2) DEFAULT 0,
    communication_allowance DECIMAL(15, 2) DEFAULT 0,
    meal_allowance DECIMAL(15, 2) DEFAULT 0,
    effective_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Payroll runs
CREATE TABLE payroll_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(id),
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    pay_date DATE NOT NULL,
    status VARCHAR(50) DEFAULT 'draft', -- 'draft', 'approved', 'processed', 'paid'
    total_gross DECIMAL(15, 2),
    total_deductions DECIMAL(15, 2),
    total_net DECIMAL(15, 2),
    created_by UUID REFERENCES users(id),
    approved_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Payroll details
CREATE TABLE payroll_details (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    payroll_run_id UUID REFERENCES payroll_runs(id) ON DELETE CASCADE,
    employee_id UUID REFERENCES employees(id),
    gross_salary DECIMAL(15, 2),
    total_allowances DECIMAL(15, 2),
    total_deductions DECIMAL(15, 2),
    income_tax DECIMAL(15, 2),
    cnps_contribution DECIMAL(15, 2),
    pension_contribution DECIMAL(15, 2),
    loan_deduction DECIMAL(15, 2),
    advance_recovery DECIMAL(15, 2),
    net_salary DECIMAL(15, 2),
    payment_status VARCHAR(50) DEFAULT 'pending',
    payslip_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Leave management
CREATE TABLE leave_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    employee_id UUID REFERENCES employees(id),
    leave_type VARCHAR(50) NOT NULL, -- 'annual', 'sick', 'maternity', 'paternity'
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    days_requested INTEGER NOT NULL,
    reason TEXT,
    status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'approved', 'rejected'
    approved_by UUID REFERENCES users(id),
    approved_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Leave balances
CREATE TABLE leave_balances (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    employee_id UUID REFERENCES employees(id),
    leave_type VARCHAR(50) NOT NULL,
    year INTEGER NOT NULL,
    entitled_days DECIMAL(5, 2),
    used_days DECIMAL(5, 2) DEFAULT 0,
    remaining_days DECIMAL(5, 2),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Attendance records
CREATE TABLE attendance_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    employee_id UUID REFERENCES employees(id),
    date DATE NOT NULL,
    clock_in TIME,
    clock_out TIME,
    break_duration INTEGER DEFAULT 0, -- minutes
    total_hours DECIMAL(5, 2),
    overtime_hours DECIMAL(5, 2) DEFAULT 0,
    status VARCHAR(50) DEFAULT 'present', -- 'present', 'absent', 'half_day', 'on_leave'
    created_at TIMESTAMP DEFAULT NOW()
);

-- Employee loans
CREATE TABLE employee_loans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    employee_id UUID REFERENCES employees(id),
    loan_amount DECIMAL(15, 2) NOT NULL,
    interest_rate DECIMAL(5, 2) DEFAULT 0,
    installment_amount DECIMAL(15, 2),
    remaining_balance DECIMAL(15, 2),
    start_date DATE NOT NULL,
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 4. API Endpoints

### Employee Endpoints
- `POST /api/v1/employees` - Create employee
- `GET /api/v1/employees` - List employees
- `GET /api/v1/employees/{id}` - Get employee details
- `PUT /api/v1/employees/{id}` - Update employee

### Payroll Endpoints
- `POST /api/v1/payroll/run` - Create payroll run
- `GET /api/v1/payroll/runs` - List payroll runs
- `POST /api/v1/payroll/run/{id}/calculate` - Calculate payroll
- `POST /api/v1/payroll/run/{id}/approve` - Approve payroll
- `POST /api/v1/payroll/run/{id}/process` - Process payments
- `GET /api/v1/payroll/payslip/{id}` - Get payslip PDF

### Leave Endpoints
- `POST /api/v1/leave/request` - Submit leave request
- `GET /api/v1/leave/requests` - List leave requests
- `PUT /api/v1/leave/request/{id}/approve` - Approve leave
- `GET /api/v1/leave/balance` - Get leave balance

### Attendance Endpoints
- `POST /api/v1/attendance/clock-in` - Clock in
- `POST /api/v1/attendance/clock-out` - Clock out
- `GET /api/v1/attendance/employee/{id}` - Employee attendance

### Employee Self-Service
- `GET /api/v1/employee-portal/profile` - My profile
- `GET /api/v1/employee-portal/payslips` - My payslips
- `GET /api/v1/employee-portal/leave-balance` - My leave balance
- `POST /api/v1/employee-portal/leave/request` - Request leave

---

## 5. Implementation Plan

### Week 1-3: Employee Master Data
- [ ] Create employee management system
- [ ] Build salary structure configuration
- [ ] Implement department management
- [ ] Create employee onboarding workflow
- [ ] Build employee directory UI

### Week 4-6: Payroll Engine
- [ ] Implement gross salary calculation
- [ ] Build allowances logic
- [ ] Create deductions engine
- [ ] Implement tax calculation (Côte d'Ivoire)
- [ ] Calculate CNPS contributions
- [ ] Build payroll run workflow

### Week 7-9: Payslip Generation
- [ ] Design payslip template
- [ ] Implement PDF generation
- [ ] Create email distribution system
- [ ] Build payslip portal
- [ ] Implement security (password protection)

### Week 10-12: Time & Attendance
- [ ] Build clock-in/out system
- [ ] Implement overtime tracking
- [ ] Create shift management
- [ ] Build attendance reports
- [ ] Integrate with payroll

### Week 13-15: Leave Management
- [ ] Create leave type configuration
- [ ] Implement leave accrual rules
- [ ] Build request/approval workflow
- [ ] Create leave balance tracking
- [ ] Build leave calendar

### Week 16-18: Employee Self-Service
- [ ] Build employee portal
- [ ] Implement payslip downloads
- [ ] Create leave request UI
- [ ] Build profile update
- [ ] Add notification system

### Week 19-20: Compliance & Reporting
- [ ] Generate CNPS declaration
- [ ] Create tax reports
- [ ] Build audit reports
- [ ] Implement payroll accounting integration
- [ ] Test compliance

---

## 6. Tax Calculation (Côte d'Ivoire)

```python
def calculate_income_tax(gross_salary: Decimal) -> Decimal:
    """
    Calculate income tax based on Côte d'Ivoire tax brackets
    Example brackets (verify with latest tax code):
    - 0 - 50,000: 0%
    - 50,001 - 130,000: 10%
    - 130,001 - 300,000: 15%
    - 300,001 - 500,000: 20%
    - 500,001+: 25%
    """
    tax = Decimal(0)
    if gross_salary <= 50000:
        tax = 0
    elif gross_salary <= 130000:
        tax = (gross_salary - 50000) * Decimal('0.10')
    elif gross_salary <= 300000:
        tax = (130000 - 50000) * Decimal('0.10') + \
              (gross_salary - 130000) * Decimal('0.15')
    elif gross_salary <= 500000:
        tax = (130000 - 50000) * Decimal('0.10') + \
              (300000 - 130000) * Decimal('0.15') + \
              (gross_salary - 300000) * Decimal('0.20')
    else:
        tax = (130000 - 50000) * Decimal('0.10') + \
              (300000 - 130000) * Decimal('0.15') + \
              (500000 - 300000) * Decimal('0.20') + \
              (gross_salary - 500000) * Decimal('0.25')
    return tax

def calculate_cnps(gross_salary: Decimal) -> Decimal:
    """
    Calculate CNPS contribution (verify rates with CNPS)
    Example: 6.3% of gross salary up to ceiling
    """
    cnps_rate = Decimal('0.063')
    cnps_ceiling = Decimal('1500000')  # Example ceiling
    taxable_salary = min(gross_salary, cnps_ceiling)
    return taxable_salary * cnps_rate
```

---

## 7. Frontend Components

**Employee Management:**
- `app/(dashboard)/employees/page.tsx`
- `components/employees/employee-table.tsx`
- `components/employees/employee-form.tsx`

**Payroll Management:**
- `app/(dashboard)/payroll/page.tsx`
- `app/(dashboard)/payroll/run/[id]/page.tsx`
- `components/payroll/payroll-run-card.tsx`
- `components/payroll/payslip-viewer.tsx`

**Employee Portal:**
- `app/(employee-portal)/layout.tsx`
- `app/(employee-portal)/dashboard/page.tsx`
- `app/(employee-portal)/payslips/page.tsx`
- `app/(employee-portal)/leave/page.tsx`

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

- ✅ Employee records created and managed
- ✅ Payroll run executed successfully
- ✅ Taxes calculated correctly
- ✅ CNPS contributions accurate
- ✅ Payslips generated and emailed
- ✅ Leave requests submitted and approved
- ✅ Attendance tracked
- ✅ Employee portal accessible
- ✅ Statutory reports generated
- ✅ All tests passing
- ✅ Deployed to staging

---

**Task Version**: 1.0  
**Estimated Duration**: 20 weeks (~5 months)  
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

