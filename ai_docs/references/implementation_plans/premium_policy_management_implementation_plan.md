# Implementation Plan - Premium Policy Management

Implement full management of Premium Policy Criteria and Policy Types for Admin users, with automatic quote generation logic.

## Proposed Changes

### Backend

#### [NEW] [premium_policy.py](file:///c:/Users/user/Desktop/Tinsur.AI/backend/app/models/premium_policy.py)
- Define `PremiumPolicyCriteria` model.
- Define `PremiumPolicyType` model.
- Define association table `premium_policy_type_criteria`.

#### [MODIFY] [__init__.py](file:///c:/Users/user/Desktop/Tinsur.AI/backend/app/models/__init__.py)
- Export the new models.

#### [NEW] [premium_policies.py](file:///c:/Users/user/Desktop/Tinsur.AI/backend/app/api/v1/endpoints/premium_policies.py)
- CRUD endpoints for `PremiumPolicyCriteria`.
- CRUD endpoints for `PremiumPolicyType`.
- Endpoint for dynamic criteria addition.

#### [MODIFY] [quotes.py](file:///c:/Users/user/Desktop/Tinsur.AI/backend/app/api/v1/endpoints/quotes.py)
- Integrate automatic quote generation logic using the new premium policy types.

### Frontend

#### [NEW] [page.tsx](file:///c:/Users/user/Desktop/Tinsur.AI/frontend/app/dashboard/admin/premium-policies/page.tsx)
- Main management page for Premium Policy Types.
- Uses `DataView` for Card/List view toggle and filtering.

#### [NEW] [premium-policy-form.tsx](file:///c:/Users/user/Desktop/Tinsur.AI/frontend/app/dashboard/admin/premium-policies/components/premium-policy-form.tsx)
- Modal form for adding/editing premium policy types.
- Includes dynamic criteria selection and addition.

#### [NEW] [criteria-form.tsx](file:///c:/Users/user/Desktop/Tinsur.AI/frontend/app/dashboard/admin/premium-policies/components/criteria-form.tsx)
- Modal form for adding/editing criteria.

#### [MODIFY] [layout.tsx](file:///c:/Users/user/Desktop/Tinsur.AI/frontend/app/dashboard/admin/layout.tsx) (If applicable)
- Add "Premium Policies" to admin navigation.

## Quote Generation Logic
The logic will evaluate client data (accidents, car age, mileage, etc.) against the `field_name`, `operator`, and `value` defined in `PremiumPolicyCriteria`.

## Verification Plan

### Automated Tests
- Create a test script `backend/app/tests/test_premium_policies.py` to:
    - Test CRUD operations for criteria and policy types.
    - Test matching logic with sample client data.
    - Run using `pytest backend/app/tests/test_premium_policies.py`.

### Manual Verification
- Navigate to Admin -> Premium Policies.
- Create several criteria based on the requirements.
- Create Premium Policy 1, 2, and 3 with their respective criteria.
- Toggle between Card and List view.
- Filter policy types by criteria.
- Register a new client and verify the automatically generated quote matches the expected policy type.
- Manually add a client as an agent and verify quote generation.
