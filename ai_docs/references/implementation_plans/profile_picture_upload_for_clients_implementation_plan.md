# Implementation Plan - Add Profile Picture Upload to Client Profile Page

This plan outlines the steps to complete the profile picture upload functionality for client profiles. While some code is already present, we will ensure it is fully integrated, follows best practices, and is verified across both list and detail views.

## Proposed Changes

### Frontend

#### [MODIFY] [client-api.ts](file:///c:/Users/user/Desktop/Insurance%20SaaS/frontend/lib/client-api.ts)
- Ensure `uploadProfilePicture` is properly exported and uses the correct `FormData` keys.

#### [MODIFY] [page.tsx](file:///c:/Users/user/Desktop/Insurance%20SaaS/frontend/app/dashboard/clients/page.tsx)
- Refactor `handleProfilePictureUpload` to use `clientApi.uploadProfilePicture` for consistency.
- Ensure the card view correctly displays the profile picture using `getProfileImageUrl`.

#### [MODIFY] [page.tsx](file:///c:/Users/user/Desktop/Insurance%20SaaS/frontend/app/dashboard/clients/[id]/page.tsx)
- Verify `handleProfilePictureUpload` is working and updating the state correctly.
- Ensure the `Avatar` component handles the "uploading" state with a loader.

#### [NEW] [ClientProfilePicture.tsx](file:///c:/Users/user/Desktop/Insurance%20SaaS/frontend/components/clients/client-profile-picture.tsx)
- Extract the profile picture upload logic and UI into a reusable component to be used in both the list and detail pages.

### Backend

#### [MODIFY] [clients.py](file:///c:/Users/user/Desktop/Insurance%20SaaS/backend/app/api/v1/endpoints/clients.py)
- Ensure the `UPLOAD_DIR` and file saving logic are robust.
- Verify the `relative_path` correctly corresponds to the static mount point.

## Verification Plan

### Automated Tests
- Create a manual verification script (Python) to simulate a profile picture upload to the backend endpoint and verify the database record.
- Run `npm run build` in the frontend to ensure no regressions in types.

### Manual Verification
1. Navigate to the Clients list page.
2. Click on a client's profile picture in either Card or List view to upload a new one.
3. Verify the picture updates immediately.
4. Navigate to a specific Client's detail page.
5. Click on the profile picture to upload a new one.
6. Verify the picture updates and persists after page refresh.
7. Verify that non-image files are rejected.
