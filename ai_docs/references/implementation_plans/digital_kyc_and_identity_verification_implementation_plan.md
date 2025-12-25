# Implementation Plan - Phase 15: Digital KYC & Identity Verification

This phase automates the secure onboarding process by using AI to parse and verify identity documents (ID Cards, Passports, Driving Licenses).

## Problem Statement
Manual entry of ID data and vehicle details is slow and prone to errors. Companies also need a reliable way to verify that information provided by clients matches their actual legal documents. Automated parsing will streamline onboarding for both self-service registration and employee-managed data entry.

## Proposed Changes

### Backend (Python/FastAPI)

#### [MODIFY] [client_details.py](file:///c:/Users/user/Desktop/Insurance%20SaaS/backend/app/models/client_details.py)
- Ensure fields match the OCR output: `vehicle_registration`, `vehicle_make`, `vehicle_model`, `vehicle_year`, `chassis_number`, `license_number`, `license_issue_date`, `license_expiry_date`.

#### [MODIFY] [client.py](file:///c:/Users/user/Desktop/Insurance%20SaaS/backend/app/models/client.py)
- Store `kyc_status`, `kyc_notes`, and `kyc_results` (to display original OCR data vs finalized system data).

#### [MODIFY] [ai_service.py](file:///c:/Users/user/Desktop/Insurance%20SaaS/backend/app/services/ai_service.py)
- Implement `parse_kyc_document(image_url: str, doc_type: str)`:
    - **Identity/DL**: Capture Full Name, ID/Licence Number, DOB, Issue Date (Valid From), Expiry.
    - **Vehicle Doc**: Capture Registration (Plate), VIN/Chassis, Make, Model, Year.
    - Detect document authenticity and expiry.

#### [NEW] [kyc.py](file:///c:/Users/user/Desktop/Insurance%20SaaS/backend/app/api/v1/endpoints/kyc.py)
- `POST /kyc/parse-document`: Generic endpoint that takes a file URL and document type, returning structured JSON for frontend auto-fill.

---

### Frontend (Next.js/TypeScript)

#### [MODIFY] [client-form-dialog.tsx](file:///c:/Users/user/Desktop/Insurance%20SaaS/frontend/components/clients/client-form-dialog.tsx)
- Add "AI Auto-fill" button in the document upload section.
- Trigger parsing on upload and automatically map fields (ID -> id_number, DOB -> date_of_birth, etc.).

#### [NEW] [client-portal-register.tsx](file:///c:/Users/user/Desktop/Insurance%20SaaS/frontend/app/portal/register/page.tsx)
- **New Feature**: Client self-service registration page.
- Guided step-by-step onboarding with integrated document scanning.
- Auto-fills registration fields as soon as the client uploads their ID or Driving License.

#### [NEW] [id-verification-card.tsx](file:///c:/Users/user/Desktop/Insurance%20SaaS/frontend/components/clients/id-verification-card.tsx)
- Reusable component to display verification status and comparison view on the client profile page.

## Verification Plan

### Automated Tests
- Create `backend/tests/test_kyc_verification.py`:
    - Mock Gemini response for a sample CNI (Ivorian ID Card) or Passport.
    - Verify that the `Client` model is updated with a "verified" or "mismatch" status based on OCR results.

### Manual Verification
- Upload test ID images through the UI.
- Verify that the AI correctly identifies expired documents and flags them in red.
