# Implementation Plan: Co-insurance Management

This plan outlines the architecture for managing policies shared between multiple insurance companies (Co-insurance).

## User Review Required

> [!IMPORTANT]
> A policy can now have multiple "Participant" insurers in addition to the "Lead" insurer (the tenant who created it). Total shares must always equal 100%.

## Proposed Changes

### Database Schema

#### [NEW] [co_insurance.py](file:///C:/Users/user/Desktop/Insurance%20SaaS/backend/app/models/co_insurance.py)
- `CoInsuranceShare` model:
    - `id`, `policy_id`, `company_id` (participant), `share_percentage`, `fee_percentage` (optional management fee).

### Backend Implementation

#### [NEW] [co_insurance.py](file:///C:/Users/user/Desktop/Insurance%20SaaS/backend/app/api/v1/endpoints/co_insurance.py)
- `GET /policies/{id}/shares`: List all participants.
- `POST /policies/{id}/shares`: Add/Update participants.
- `DELETE /policies/{id}/shares/{share_id}`: Remove a participant.

#### [MODIFY] [claims.py](file:///C:/Users/user/Desktop/Insurance%20SaaS/backend/app/api/v1/endpoints/claims.py)
- Update claim approval logic to automatically generate "Inter-company settlements" for co-insurance participants based on their shares.

### Frontend Implementation

#### [MODIFY] [policies/[id]/page.tsx](file:///C:/Users/user/Desktop/Insurance%20SaaS/frontend/app/dashboard/policies/%5Bid%5D/page.tsx)
- Add a "Co-insurance" card or tab.
- Display a list of participating companies and their percentages.
- Implementation of a modal to manage these shares.

---

## Verification Plan

### Automated Tests
- `pytest backend/tests/api/test_coinsurance.py`: Test share validation (must sum to 100).
- Test premium distribution calculations.

### Manual Verification
1. Create a policy with 30% share given to "Company B".
2. File a $10,000 claim.
3. Verify that a $3,000 settlement is generated for "Company B".
