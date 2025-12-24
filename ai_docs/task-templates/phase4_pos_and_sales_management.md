# AI Task Planning Template - Phase 4: POS & Sales Management

> **About This Task:** This phase implements Point of Sale management, multi-channel sales tracking, comprehensive sales analytics, employee performance dashboards, commission management, and inventory tracking.

---

## 1. Task Overview

### Task Title
**Title:** Phase 4: POS & Sales Management - Sales Analytics & Performance Tracking

### Goal Statement
**Goal:** Build a comprehensive POS management system with location tracking, multi-channel sales (online vs. offline), detailed employee performance analytics, automated commission calculations, sales leaderboards, inventory management, and advanced sales reporting. This enables insurance companies to track and optimize their physical locations and sales forces.

---

## 2. Success Criteria

- [x] POS locations registered and managed
- [x] Sales tracked by channel (POS, online, agent, mobile app)
- [x] Employee sales performance dashboards operational
- [x] Daily, weekly, monthly, yearly sales reports generated
- [x] Commission calculations automated
- [x] Sales leaderboards displaying top performers
- [x] Inventory tracked for marketing materials
- [x] Geographic sales heat maps displayed
- [x] Real-time sales monitoring dashboard
- [x] Channel attribution reports available

---

## 3. Database Schema

```sql
-- POS locations
CREATE TABLE pos_locations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(id),
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50) UNIQUE NOT NULL,
    address TEXT,
    city VARCHAR(100),
    region VARCHAR(100),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    operating_hours JSONB,
    manager_id UUID REFERENCES users(id),
    capacity INTEGER,
    services_offered JSONB,
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Sales transactions
CREATE TABLE sales_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(id),
    policy_id UUID REFERENCES policies(id),
    employee_id UUID REFERENCES users(id),
    pos_location_id UUID REFERENCES pos_locations(id),
    channel VARCHAR(50) NOT NULL, -- 'pos', 'online', 'agent', 'mobile', 'partner'
    sale_amount DECIMAL(15, 2) NOT NULL,
    commission_amount DECIMAL(15, 2),
    sale_date DATE NOT NULL,
    sale_time TIME NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Employee sales targets
CREATE TABLE sales_targets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    employee_id UUID REFERENCES users(id),
    period VARCHAR(50), -- 'daily', 'weekly', 'monthly', 'yearly'
    target_amount DECIMAL(15, 2),
    target_count INTEGER,
    start_date DATE,
    end_date DATE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Inventory items
CREATE TABLE inventory_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pos_location_id UUID REFERENCES pos_locations(id),
    item_name VARCHAR(255) NOT NULL,
    item_type VARCHAR(100), -- 'brochure', 'form', 'equipment', etc.
    quantity INTEGER DEFAULT 0,
    min_quantity INTEGER DEFAULT 10,
    last_restocked DATE,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 4. API Endpoints

### POS Endpoints (`/api/v1/pos`)
- `POST /pos/locations` - Create POS location
- `GET /pos/locations` - List POS locations
- `GET /pos/locations/{id}` - Get POS details
- `GET /pos/locations/{id}/sales` - Get sales by location
- `GET /pos/locations/{id}/performance` - Get performance metrics

### Sales Endpoints (`/api/v1/sales`)
- `POST /sales/transactions` - Record sale
- `GET /sales/transactions` - List sales with filters
- `GET /sales/analytics` - Get sales analytics
- `GET /sales/reports/daily` - Daily sales report
- `GET /sales/reports/weekly` - Weekly sales report
- `GET /sales/reports/monthly` - Monthly sales report
- `GET /sales/reports/yearly` - Yearly sales report
- `GET /sales/by-channel` - Sales by channel
- `GET /sales/by-employee` - Sales by employee

### Employee Performance Endpoints
- `GET /api/v1/performance/employee/{id}` - Individual performance
- `GET /api/v1/performance/leaderboard` - Sales leaderboard
- `GET /api/v1/performance/targets` - Targets vs. actuals

### Commission Endpoints
- `GET /api/v1/commissions/calculate` - Calculate commissions
- `GET /api/v1/commissions/employee/{id}` - Employee commissions
- `POST /api/v1/commissions/approve` - Approve commission payout

---

## 5. Implementation Plan

### Week 1-3: POS Infrastructure
- [ ] Create POS location management
- [ ] Implement geographic mapping
- [ ] Create POS assignment workflows
- [ ] Build POS configuration UI

### Week 4-6: Sales Tracking
- [ ] Implement sales transaction recording
- [ ] Create channel attribution logic
- [ ] Build sales recording UI
- [ ] Test multi-channel tracking

### Week 7-9: Analytics & Reporting
- [ ] Build sales analytics engine
- [ ] Create report generation logic
- [ ] Implement data aggregation
- [ ] Build visualization components
- [ ] Create sales dashboards

### Week 10-12: Employee Performance
- [ ] Create target management
- [ ] Build leaderboard logic
- [ ] Implement performance calculations
- [ ] Create performance dashboards
- [ ] Build mobile performance app

### Week 13-15: Commission System
- [ ] Define commission structures
- [ ] Implement calculation logic
- [ ] Create approval workflows
- [ ] Build commission reports
- [ ] Test payouts

### Week 16: Inventory & Finalization
- [ ] Create inventory management
- [ ] Implement reorder alerts
- [ ] Build inventory tracking UI
- [ ] Test and deploy

---

## 6. Frontend Components

**POS Components:**
- `app/(dashboard)/pos/locations/page.tsx`
- `components/pos/location-map.tsx`
- `components/pos/location-card.tsx`

**Sales Components:**
- `app/(dashboard)/sales/dashboard/page.tsx`
- `components/sales/sales-chart.tsx`
- `components/sales/channel-comparison.tsx`
- `components/sales/heat-map.tsx`

**Performance Components:**
- `app/(dashboard)/performance/leaderboard/page.tsx`
- `components/performance/employee-card.tsx`
- `components/performance/target-progress.tsx`

---

## 7. Key Features

### Sales Analytics:
- Daily/Weekly/Monthly/Yearly aggregations
- Product mix analysis per POS
- Conversion rates (quotes to policies)
- Peak hours analysis
- Geographic penetration
- Customer demographics

### Employee Performance:
- Individual sales statistics
- Commission earned tracking
- Sales velocity metrics
- Customer satisfaction scores
- Training completion status
- Performance trends

### Comparative Analytics:
- POS vs. Online performance
- Channel ROI comparison
- Cost per acquisition by channel
- Retention rates by channel

---

## 8. Mandatory Rules & Best Practices

Follow ALL rules from Phase 1 and `ai_task_template_skeleton.md`.

### New Mandatory Rules

#### Verify Component Integrity (MANDATORY)
**File:** `verify_component_integrity.mdc`

**Checklist:**
- [ ] **Check Filesystem**: Run `Test-Path` or `ls` on the component path.
- [ ] **Check Package.json**: Ensure underlying libs (e.g., `@radix-ui/react-toast`) are installed.
- [ ] **Fix First**: If missing, install/create BEFORE adding the import.

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

#### Verify API Response Consistency
**File:** `api_response_consistency.mdc`

**Checklist:**
- [ ] **Check Backend Model**: Does returned Pydantic model have `List[...]` or `{ items: ..., total: ... }`?
- [ ] **Align Frontend Client**: If backend returns Object, client MUST unwrap it if component expects Array.
- [ ] **Verify Usage**: Check if `map()` is called on the result. If so, result must be Array.

---

## 9. Definition of Done

- ✅ POS locations created and managed
- ✅ Sales recorded across all channels
- ✅ Daily/Weekly/Monthly reports generated
- ✅ Employee leaderboards displayed
- ✅ Commissions calculated automatically
- ✅ Sales dashboards operational
- ✅ Inventory tracked and alerts working
- ✅ Heat maps showing geographic sales
- ✅ All tests passing
- ✅ Deployed to staging

---

**Task Version**: 1.0  
**Estimated Duration**: 16 weeks (~4 months)  
**Status**: Ready for Implementation
