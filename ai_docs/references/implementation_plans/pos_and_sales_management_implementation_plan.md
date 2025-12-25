# Implementation Plan: Phase 4 - POS & Sales Management

This plan outlines the steps to implement the Point of Sale (POS) and Sales Management module, focusing on location management, sales attribution, commission tracking, and analytics.

## Proposed Changes

### Backend Models & Database
#### [NEW] [pos_location.py](file:///c:/Users/user/Desktop/Insurance%20SaaS/backend/app/models/pos_location.py)
- Create `POSLocation` model to store physical POS details.
- Fields: `id`, `company_id`, `name`, `address`, `city`, `region`, `manager_id`, `is_active`, `created_at`, `updated_at`.

#### [NEW] [commission.py](file:///c:/Users/user/Desktop/Insurance%20SaaS/backend/app/models/commission.py)
- Create `Commission` model to track agent/broker earnings.
- Fields: `id`, `company_id`, `agent_id`, `policy_id`, `amount`, `status` (pending, paid), `paid_at`.

#### [NEW] [pos_inventory.py](file:///c:/Users/user/Desktop/Insurance%20SaaS/backend/app/models/pos_inventory.py)
- Create `POSInventory` model for physical materials.
- Fields: `id`, `pos_location_id`, `item_name`, `quantity`, `low_stock_threshold`.

#### [MODIFY] [user.py](file:///c:/Users/user/Desktop/Insurance%20SaaS/backend/app/models/user.py)
- Add `pos_location_id` (ForeignKey to `pos_locations.id`) to track which POS an employee belongs to.

#### [MODIFY] [policy.py](file:///c:/Users/user/Desktop/Insurance%20SaaS/backend/app/models/policy.py)
- Add `sale_channel` (String: 'online', 'pos', 'agent', 'broker').
- Add `pos_location_id` (ForeignKey to `pos_locations.id`).

#### [MODIFY] [quote.py](file:///c:/Users/user/Desktop/Insurance%20SaaS/backend/app/models/quote.py)
- Add `sale_channel` and `pos_location_id` to match `Policy`.

---

### Backend API & Schemas
#### [NEW] [pos_location.py](file:///c:/Users/user/Desktop/Insurance%20SaaS/backend/app/schemas/pos_location.py)
#### [NEW] [commission.py](file:///c:/Users/user/Desktop/Insurance%20SaaS/backend/app/schemas/commission.py)
#### [NEW] [pos_inventory.py](file:///c:/Users/user/Desktop/Insurance%20SaaS/backend/app/schemas/pos_inventory.py)
- Define Pydantic schemas for the new models.

#### [NEW] [pos.py](file:///c:/Users/user/Desktop/Insurance%20SaaS/backend/app/api/v1/endpoints/pos.py)
- Implement CRUD endpoints for POS locations and inventory.

#### [NEW] [sales_reports.py](file:///c:/Users/user/Desktop/Insurance%20SaaS/backend/app/api/v1/endpoints/sales_reports.py)
- Implement sales analytics endpoints (daily/weekly/monthly summaries, channel attribution).

---

### Frontend Components
#### [NEW] [POS Management Page](file:///c:/Users/user/Desktop/Insurance%20SaaS/frontend/app/dashboard/pos/page.tsx)
- UI to list, create, and edit POS locations.

#### [NEW] [Sales Analytics Page](file:///c:/Users/user/Desktop/Insurance%20SaaS/frontend/app/dashboard/sales/page.tsx)
- Charts (Recharts) for sales volume, channel breakdown, and POS performance.

#### [NEW] [Leaderboard Component](file:///c:/Users/user/Desktop/Insurance%20SaaS/frontend/components/sales/Leaderboard.tsx)
- Display top-performing agents/POS locations.

---

## Verification Plan

### Automated Tests
- **Unit Test**: Commission calculation logic.
- **Integration Test**: Create a quote/policy via POS and verify attribution in sales reports.
- **Command**: `pytest backend/tests/test_pos_flow.py` (to be created)

### Manual Verification
- Log in as Company Admin.
- Create a new POS Location.
- Assign an Agent to that POS.
- Create a Policy as that Agent and verify it appears in the Sales Dashboard under the correct POS.
- Check the Sales leaderboard for updated rankings.
