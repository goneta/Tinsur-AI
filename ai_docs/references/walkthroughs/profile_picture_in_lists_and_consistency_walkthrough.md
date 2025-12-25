# Profile Picture Management Enhancements

I have enhanced the employee and client management interfaces to provide consistent profile picture management across all views.

## Key Changes

### 1. Interactive List View Columns
The "List" view (DataTable) for both **Employees** and **Clients** now includes a Profile Picture column at the start.
- **Interactive Avatars**: Clicking the avatar or the camera icon overlay in the list view triggers the file upload process, just like in the Card view.
- **Visual Feedback**: A loading spinner appears within the avatar when an upload is in progress.

### 2. Centralized Image URL Logic
- Moved `getProfileImageUrl` to `frontend/lib/api.ts` to ensure consistent URL construction across all components and avoid code duplication.

### 3. UI Consistency
- The Card/List toggle and Search functionality are now identical for both Employees and Clients.
- Improved the spacing and alignment of the new columns in the data tables.

## Verification Results

### Desktop View
- [x] Verified that the "List" view shows the profile picture column.
- [x] Verified that clicking the column triggers the file picker.
- [x] Verified that successful uploads update the image in both Card and List views simultaneously.
- [x] Verified that searched/filtered results still allow image uploads.

### API Integration
- [x] Confirmed that the `profile_picture` field is correctly handled by the backend for both models.
- [x] Confirmed that the `uploads/clients` and `uploads/profiles` directories are correctly used.

> [!TIP]
> You can now quickly update multiple profile pictures without switching back and forth between "Card" and "List" views, making bulk management easier.
