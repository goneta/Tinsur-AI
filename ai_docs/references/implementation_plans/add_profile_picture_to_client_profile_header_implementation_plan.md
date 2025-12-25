# Implementation Plan - Add Profile Picture to Client Profile Page

Add a circular profile picture to the client profile page header, positioned to the right of the client name and badges, following the aesthetic of the provided reference image.

## Proposed Changes

### Frontend

#### [MODIFY] [page.tsx](file:///c:/Users/user/Desktop/Insurance%20SaaS/frontend/app/dashboard/clients/%5Bid%5D/page.tsx)
-   Import `Avatar`, `AvatarImage`, and `AvatarFallback` from `@/components/ui/avatar`.
-   Import `getProfileImageUrl` from `@/lib/api`.
-   Update the header section to include the circular profile picture.
-   The profile picture will be styled with a "reasonable size" (e.g., `h-20 w-20`) and `rounded-full`.
-   It will be placed within the flex container of the header, to the right of the name and badges block.

## Verification Plan

### Manual Verification
1.  Run the frontend and backend services.
2.  Navigate to the client list: `http://localhost:3000/dashboard/clients`.
3.  Click on a client to view their profile.
4.  Verify that a circular profile picture (or fallback) is visible in the header, to the right of the name.
5.  If the client has a profile picture, verify it renders correctly.
6.  If not, verify the fallback (initials or icon) renders.

### Automated Tests
-   No automated tests are planned for this UI change as it's primarily aesthetic.
