# Collaboration Hub Enhancements

This plan outlines the implementation of the complex document sharing system requested by the user, including granular permissions (A/B/C), scoping (B2B, B2C, etc.), and A2A agent integration.

## Database Changes

### `Document` Model Updates
- Add `label` enum: 'Quote', 'Policy', 'Receipt', 'Payslip', 'Document', 'Ads', 'Driving Licence', 'Car Papers', 'Photo'.
- Add `file_type` (already likely exists, verify coverage of required list).

### `DocumentShare` Model (New/Refactor)
Stores the active sharing state of a document.
- `document_id`: FK to Document
- `shared_by_company_id`: FK to Company
- `visibility`: 'PUBLIC', 'PRIVATE'
- `scope`: 'B2B', 'B2C', 'B2E', 'E2E', 'C2C' (Nullable if Public)
- `sharing_option`: 'NOT_SHAREABLE' (1), 'SHAREABLE' (2)
- `reshare_rule`: 'A' (Can share extended), 'B' (Can share once), 'C' (Cannot share) (Nullable)
- `status`: 'ACTIVE', 'REVOKED'

## Backend Agents

### `a2a_document_agent`
A new agent responsible for enforcing sharing rules.
- **Capabilities**:
    - `share_document(doc_id, visibility, scope, options)`: Creates share record.
    - `revoke_access(doc_id)`: Marks shares as revoked.
    - `get_available_documents(user_context)`: Returns docs user has access to, filtering by Scope (B2B/B2C logic) and Reshare Rules.
    - `validate_reshare(doc_id, user_context)`: Checks if user can reshare based on constraints (A/B/C).

## Frontend Enhancements

### `CollaborationPage`
- **Tabs**: "My Documents", "Public Dataset", "Shared with Me".
- **Upload Wizard**:
    1. Select File.
    2. Choose Label.
    3. Configure Sharing (Public vs Private -> Scope -> Options).
- **Listing View**:
    - Columns: Name, Label, Owner, Shared Date, Actions.
    - Actions: "Reshare" (if permitted), "Revoke" (if owner), "Download".

## User Management (Phase 12)

### Backend
#### [NEW] [users.py](file:///c:/Users/user/Desktop/Insurance%20SaaS/backend/app/api/v1/endpoints/users.py)
- `GET /users`: List users (Paginated, Filter by Role/Search).
- `POST /users`: Create user (Invite flow).
- `PUT /users/{id}`: Update user (Role, Active Status).
- `DELETE /users/{id}`: Deactivate user.

### Frontend
#### [NEW] [user-api.ts](file:///c:/Users/user/Desktop/Insurance%20SaaS/frontend/lib/user-api.ts)
- API methods for user management.

#### [NEW] [user-management.tsx](file:///c:/Users/user/Desktop/Insurance%20SaaS/frontend/components/admin/user-management.tsx)
- Data Table for users.
- Actions: Edit Role, Deactivate, Reset Password (optional).

#### [NEW] [user-dialog.tsx](file:///c:/Users/user/Desktop/Insurance%20SaaS/frontend/components/admin/user-dialog.tsx)
- Form to add new user (Email, First/Last Name, Role).
- Edit mode for existing users.

## Verification Plan
1. **Upload & Label**: Verify all label types and file types are accepted.
2. **Permission Logic**:
    - **Scenario 1**: User A shares Doc 1 as **Private (B2B), Option 1 (Not Shareable)** with User B. Verify User B can view but NOT reshare.
    - **Scenario 2**: User A shares Doc 2 as **Private (B2C), Option 2 (Shareable), Type A** with User B. Verify User B can reshare.
    - **Scenario 3**: User A changes Doc 1 to **Revoked**. Verify User B immediately loses access.
