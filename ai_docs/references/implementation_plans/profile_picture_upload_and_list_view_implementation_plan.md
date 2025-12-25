# Profile Picture Upload Implementation Plan

This plan outlines the steps to allow users to upload profile pictures for employees by clicking the camera icon on the employee card.

## Proposed Changes

### Backend

#### [MODIFY] [backend/app/models/user.py](file:///c:/Users/user/Desktop/Insurance%20SaaS/backend/app/models/user.py)
- Add `profile_picture` column (String, nullable) to the `User` model.

#### [MODIFY] [backend/app/schemas/user.py](file:///c:/Users/user/Desktop/Insurance%20SaaS/backend/app/schemas/user.py)
- Add `profile_picture: Optional[str] = None` to `UserResponse`, `UserUpdate`, and `UserBase` (if appropriate).

#### [MODIFY] [backend/app/api/v1/endpoints/users.py](file:///c:/Users/user/Desktop/Insurance%20SaaS/backend/app/api/v1/endpoints/users.py)
- Create a new endpoint `POST /users/{user_id}/profile-picture`.
- Accepts a file upload (`UploadFile`).
- Validates the user exists and the requestor has permission (admin/manager or self).
- Saves the file to `uploads/profiles/`.
- Updates the `User.profile_picture` field with the file URL/path.
- Returns the updated User object or the URL.

#### [MODIFY] [backend/app/main.py](file:///c:/Users/user/Desktop/Insurance%20SaaS/backend/app/main.py)
- Ensure the `uploads` directory is served statically so images can be accessed by the frontend.
- (Verify if this is already done for documents, otherwise add it).

### Frontend

#### [MODIFY] [frontend/app/dashboard/employees/page.tsx](file:///c:/Users/user/Desktop/Insurance%20SaaS/frontend/app/dashboard/employees/page.tsx)
- **UI Update**:
    - Wrap the Avatar/Camera icon in a clickable label or button that triggers a hidden file input.
    - OR use a `useRef` to trigger the file input click programmatically.
- **Logic**:
    - `handleFileChange` function calls the upload API.
    - On success, update the local `employees` state to reflect the new image immediately.
    - Show a loading state (spinner or opacity change) during upload.

## Verification Plan

### Manual Verification
1.  **Upload Flow**:
    - Click the camera icon on an employee card.
    - Select an image (JPG/PNG).
    - Verify strict visual feedback (loading).
    - Verify the image appears in the circle after upload.
2.  **Persistence**:
    - Refresh the page -> Image should still be there.
    - Check "List View" -> Image/Avatar should (optional but good) show there too if we add avatar to list.
3.  **Permissions**:
    - Try as Admin (should work).

