# Walkthrough: Phase 4 - POS & Sales Management

I have implemented the Point of Sale (POS) and Sales Management module.

## Changes

### Backend
- **New Models**: 
    - `POSLocation`: Stores details about physical locations.
    - `Commission`: Tracks earnings for agents/brokers.
    - `POSInventory`: Manages stock at POS locations.
- **Updated Models**:
    - `User`: Added `pos_location_id`.
    - `Policy` & `Quote`: Added `sale_channel` and `pos_location_id`.
- **New APIs**: 
    - `/api/v1/pos`: Endpoints for locations and inventory.
    - `/api/v1/sales-reports`: Endpoints for analytics and leaderboards.

### Frontend
- **POS Management**: New page at `/dashboard/pos` to list and create POS locations.
- **Sales Analytics**: New page at `/dashboard/sales` displaying:
    - Total Revenue & Sales Count
    - Sales by Channel (Bar & Pie Charts)
    - Top Agents Leaderboard

## Verification

### Verification Results
- **Migrations**: Success (POS tables created).
- **Backend**: API reachable, but requires RESTART to pick up new models.
- **Frontend**: Dependency `recharts` installed.

### Verification Script
I created a script `backend/tests/manual_test_pos.py`.
> **Note**: You must **restart the backend server** before running this script, as the running instance does not have the new `POSLocation` models loaded.

Run:
```bash
python backend/tests/manual_test_pos.py
```
