# Implementation Plan: QR Verification System

This plan outlines the architecture and steps to implement the QR Verification system, allowing third parties to securely verify insurance policies.

## User Review Required

> [!IMPORTANT]
> A new public API route `/api/v1/public/verify/{token}` will be exposed. It will only return non-sensitive verification data (Status, Policy Number, Expiry Date, Client Initials) to protect privacy.

## Proposed Changes

### Backend Implementation

#### [MODIFY] [policy.py](file:///C:/Users/user/Desktop/Insurance%20SaaS/backend/app/models/policy.py)
- Ensure `qr_code_data` is used for storing the secure verification token.
- Add a utility method to the `Policy` model or a service to generate a secure HMAC-based verification token.

#### [NEW] [qr_verification.py](file:///C:/Users/user/Desktop/Insurance%20SaaS/backend/app/api/v1/endpoints/qr_verification.py)
- `POST /generate/{policy_id}`: Generate a QR code token and URL for a policy (Internal/Agent use).
- `GET /verify/{token}`: Public endpoint to return policy status and basic info.

#### [MODIFY] [backend/app/main.py](file:///C:/Users/user/Desktop/Insurance%20SaaS/backend/app/main.py)
- Register the new public verification router.

### Frontend Implementation

#### [NEW] [verify/[token]/page.tsx](file:///C:/Users/user/Desktop/Insurance%20SaaS/frontend/app/verify/%5Btoken%5D/page.tsx)
- Create a mobile-friendly, public verification results page.
- Show "VERIFIED" with a green badge and policy details if the token is valid.
- Show "INVALID" or "EXPIRED" if the policy is inactive.

#### [MODIFY] [policies/[id]/page.tsx](file:///C:/Users/user/Desktop/Insurance%20SaaS/frontend/app/dashboard/policies/%5Bid%5D/page.tsx)
- Add a "Print Verification QR" button or display the QR code directly on the policy view.

---

## Verification Plan

### Automated Tests
- `pytest backend/tests/api/test_qr_verification.py`: Test token generation and public verification endpoint.

### Manual Verification
- Generate a QR code for a test policy.
- Access the verification URL directly to see the public status page.
- Change the policy status to "EXPIRED" and verify the public page updates accordingly.
