# Sharecode System Implementation Plan

## Goal Description
Implement a secure document sharing authorization system called "Sharecode". This system requires users to generate a unique code (QR + Alphanumeric) to authorize sharing with specific recipients. This acts as a handshake mechanism before documents can be shared in the collaboration tab.

## User Review Required
> [!IMPORTANT]
> **Recipient Identification**: I am assuming "Recipients" in the selection list are existing `User` or `Client` entities in the system. I will implement the recipient selector to fetch available users/clients based on the selected Share Type (e.g. B2B -> Companies, B2C -> Clients).
> **QR Code**: On the web platform, we will generate and display the QR code image. The actual scanning capability is for the mobile app, but we will provide the "Enter Code" input for the web platform as requested.

## Proposed Changes

### Backend

#### [NEW] [share_code.py](file:///c:/Users/user/Desktop/Insurance%20SaaS/backend/app/models/share_code.py)
- Define `ShareCode` SQLAlchemy model:
    - `id`: UUID (PK)
    - `code`: String (Unique, Alphanumeric)
    - `creator_id`: UUID (FK to User)
    - `share_type`: Enum (B2B, B2C, B2E, E2C, E2E, C2C)
    - `recipient_ids`: JSON/Array (List of authorized user/client IDs)
    - `status`: String/Enum (active, revoked, used)
    - `expires_at`: DateTime
    - `created_at`: DateTime

#### [NEW] [share_code.py](file:///c:/Users/user/Desktop/Insurance%20SaaS/backend/app/schemas/share_code.py)
- Define Pydantic models:
    - `ShareCodeCreate`: input `share_type`, `recipient_ids`.
    - `ShareCodeResponse`: output includes `code`, `qr_code_base64` (or URL), `recipients` details.
    - `ShareCodeValidate`: input `code`.

#### [NEW] [share_code.py](file:///c:/Users/user/Desktop/Insurance%20SaaS/backend/app/api/v1/endpoints/share_code.py)
- `POST /share-codes`: Generate a new share code.
    - Generates a unique 6-digit alphanumeric code.
    - Generates a QR code image (using a library like `qrcode`).
    - Saves to DB.
- `GET /share-codes`: List share codes created by the current user.
- `DELETE /share-codes/{id}`: Revoke a share code.
- `POST /share-codes/validate`: Endpoint for a recipient to enter the code.
    - Validates if the current user is in `recipient_ids`.
    - If valid, potentially creates an `InterCompanyShare` or similar authorization record (or just returns success to unlock UI).

#### [MODIFY] [api.py](file:///c:/Users/user/Desktop/Insurance%20SaaS/backend/app/api/api.py)
- Include the new `share_code` router.

### Frontend

#### [NEW] [DisplayShareCode.tsx](file:///c:/Users/user/Desktop/Insurance%20SaaS/frontend/components/sharecode/DisplayShareCode.tsx)
- Component to show the QR code and alphanumeric code prominently.

#### [NEW] [CreateShareCodeModal.tsx](file:///c:/Users/user/Desktop/Insurance%20SaaS/frontend/components/sharecode/CreateShareCodeModal.tsx)
- Modal with:
    - Dropdown for Share Type (B2B, B2C, etc.).
    - Checkbox list for Recipients (mocked or fetched from backend).
    - "Generate" button.
- Calls `POST /share-codes`.

#### [NEW] [ShareCodeList.tsx](file:///c:/Users/user/Desktop/Insurance%20SaaS/frontend/components/sharecode/ShareCodeList.tsx)
- Table/List showing active Sharecodes.
- Actions: Delete, View, Send.

#### [NEW] [page.tsx](file:///c:/Users/user/Desktop/Insurance%20SaaS/frontend/app/dashboard/settings/share-code/page.tsx)
- New settings page for "Sharecode Management".
- Includes `ShareCodeList` and a button to open `CreateShareCodeModal`.

## Verification Plan

### Automated Tests
- I will verify the backend API using `curl` or a test script.
    - `POST /share-codes` -> should return code + QR.
    - `GET /share-codes` -> should list it.
    - `DELETE /share-codes/{id}` -> should revoke it.

### Manual Verification
1.  **Generate Code**:
    - Go to Settings -> Sharecode.
    - Click "Create Sharecode".
    - Select Type and Recipient.
    - Click Generate.
    - Verify QR code and text code appear.
2.  **List Codes**:
    - Verify the new code appears in the list.
3.  **Revoke Code**:
    - Click Delete/Revoke.
    - Verify it disappears or status changes.
4.  **Validate Code (Mock)**:
    - Use a separate browser/incognito or mock the request to `POST /validate` with the generated code.
