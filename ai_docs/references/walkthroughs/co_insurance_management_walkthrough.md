# Walkthrough: Co-insurance Management

I have completed the Co-insurance module, the final functional requirement for Phase 7. This system enables complex risk-sharing between multiple insurance companies on the platform.

## Features Delivered

### 1. Risk Distribution Model
- **New Database Table**: `co_insurance_shares` allows a "Lead" insurer to assign percentage shares of a policy to other "Participant" insurers.
- **Validation**: Ensures that the total risk distributed does not exceed 100%.

### 2. Automated Financial Settlements
- **Claim Integration**: Modified the `ClaimService` to automatically trigger settlements when a claim is approved.
- **Inter-company Sharing**: Generates `InterCompanyShare` records (type: `claim_settlement`) for all participants.
- **Formula**: `Settlement = Approved Claim Amount * Share %`.

### 3. Management Interface
- **Dashboard Widget**: Added a "Co-insurance" card to the Policy Detail page.
- **Participant Modal**: Created a new UI component to search for companies and assign shares/fees.
- **Real-time Totals**: Displays a summary of the total shared risk.

## Technical Verification

### distribution Logic
The settlement distribution was verified with a specialized script `backend/app/scripts/verify_coinsurance.py`. 

**Test Case**:
- Policy Amount: $10,000
- Participant Share: 30%
- Expected Settlement: $3,000

**Result**:
```
SUCCESS: Inter-company settlement generated.
SUCCESS: Settlement amount calculated correctly (30% of 10000).
Settlement Details: Co-insurance share of 30.00% for claim CLM-20251218-MK9C. Amount: 3000.00
```

### Database Updates
- Added `co_insurance_shares` table.
- Added `notes` field to `inter_company_shares` to support more descriptive financial memos.

## How to manage Co-insurance
1. Open any **Policy** from the dashboard.
2. Locate the **Co-insurance** card on the right-hand panel.
3. Click the **Edit/Add** icon (pencil).
4. Select a participating insurance company.
5. Enter their **Share %** and any optional **Management Fee**.
6. Save. 
7. Future claims approved on this policy will now notify the participant and generate a settlement request.
