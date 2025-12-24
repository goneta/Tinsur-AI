# Tasks: Co-insurance Management Implementation

- [x] Planning & Design [x]
    - [x] Create `implementation_plan.md` for Co-insurance
- [x] Database Implementation [x]
    - [x] Create `co_insurance_shares` table/model
    - [x] Update `Policy` model with co-insurance relationships
    - [x] Run database migrations
- [x] Backend Implementation [x]
    - [x] Create API endpoints for managing co-insurance shares
    - [x] Implement logic for premium distribution based on shares
    - [x] Implement logic for claim settlement distribution based on shares
    - [x] Update `ClaimsAgent` to handle co-insurance scenarios (Settlement generation logic added to ClaimService)
- [x] Frontend Implementation [x]
    - [x] Add Co-insurance management section to Policy Details
    - [x] Create UI for adding/editing participants and percentages
    - [x] Display share breakdown in financial views
- [x] Verification & Testing [x]
    - [x] Test share distribution calculations
    - [x] E2E test for co-insured policy claim settlement (Verified with script)
