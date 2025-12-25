# Sharecode System Walkthrough

I have implemented the **Sharecode** system to allow secure document sharing authorization.

## Features Implemented

### Backend
- **New Model**: `ShareCode` (stores code, type, recipients, status).
- **API Endpoints**:
    - `POST /api/v1/share-codes/`: Generate a new code with QR.
    - `GET /api/v1/share-codes/`: List active codes.
    - `DELETE /api/v1/share-codes/{id}`: Revoke a code.
    - `POST /api/v1/share-codes/validate`: Validate a code (for recipient).

### Frontend
- **Settings Page**: New "Sharecode" tab under Settings.
- **Generate Modal**: Allows selecting "Share Type" (B2B, B2C, etc.) and Recipients.
- **List View**: Shows active codes, QR thumbnails, and recipient counts.
- **Revoke Action**: Allows deleting/revoking a sharecode.

## Verification Steps

1.  **Navigate to Sharecode Settings**:
    - Go to `/dashboard/settings/share-code`.
    - You should see the empty state or list of existing codes.

2.  **Generate a Code**:
    - Click "Create Sharecode".
    - Select a Share Type (e.g., B2B).
    - Select one or more recipients from the list.
    - Click "Generate Sharecode".

3.  **Verify Output**:
    - A new row should appear in the list.
    - You should see a QR code thumbnail and a 6-digit alphanumeric code.
    - Click the "View" (Eye icon) button to see the large QR code.

4.  **Revoke a Code**:
    - Click the "Trash" icon on a code row.
    - Confirm the code is removed from the list (or status changes).

## Next Steps
- Implement actual recipient fetching from the backend (currently mocked).
- Integrate the "Validate Code" flow for the recipient side (entering the code).
