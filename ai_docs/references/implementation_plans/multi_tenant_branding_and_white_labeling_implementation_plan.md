# Implementation Plan - Multi-tenant Branding & White-labeling

This plan outlines the steps required to implement Phase 11, allowing Company Admins to customize their platform's branding (logo and colors) and ensuring the frontend dynamically applies these settings.

## Proposed Changes

### Backend

#### [MODIFY] [company.py](file:///c:/Users/user/Desktop/Insurance%20SaaS/backend/app/models/company.py)
- Add `primary_color` and `secondary_color` columns to the `Company` model (String(10), nullable).

#### [MODIFY] [company.py](file:///c:/Users/user/Desktop/Insurance%20SaaS/backend/app/schemas/company.py)
- Update `CompanyResponse` and `CompanyUpdate` schemas to include `primary_color` and `secondary_color`.

#### [NEW] [Migration]
- Create an Alembic migration to add the new columns to the `companies` table.

---

### Frontend

#### [MODIFY] [settings.ts](file:///c:/Users/user/Desktop/Insurance%20SaaS/frontend/types/settings.ts)
- Update `CompanySettings` and `CompanyUpdateRequest` interfaces to include `primary_color` and `secondary_color`.

#### [MODIFY] [page.tsx](file:///c:/Users/user/Desktop/Insurance%20SaaS/frontend/app/dashboard/settings/company/page.tsx)
- Add color pickers for Primary and Secondary brand colors.
- Update the save logic to include these new fields.

#### [NEW] [branding-provider.tsx](file:///c:/Users/user/Desktop/Insurance%20SaaS/frontend/components/branding-provider.tsx)
- Create a context provider that injects CSS variables (`--primary`, `--secondary`, etc.) into the document based on the company's settings.
- It will listen for changes to the company settings and update the variables dynamically.

#### [MODIFY] [layout.tsx](file:///c:/Users/user/Desktop/Insurance%20SaaS/frontend/app/layout.tsx)
- Wrap the application with `BrandingProvider`.

#### [MODIFY] [Sidebar.tsx](file:///c:/Users/user/Desktop/Insurance%20SaaS/frontend/components/dashboard/Sidebar.tsx) (and Header)
- Update the logo display logic to use `company.logo_url` if available, falling back to the default logo.

## Verification Plan

### Automated Tests
- Run backend linting and type checks.
- Run frontend build to ensure no breaking changes in types or components.

### Manual Verification
1.  **Settings Update**:
    - Navigate to Dashboard > Settings > Company.
    - Upload a logo and select new primary/secondary colors.
    - Click "Save Changes".
    - Verify that the settings are persisted (refresh the page).
2.  **Dynamic Theming**:
    - Verify that the primary buttons, sidebar accents, and other themed elements reflect the selected colors immediately or after refresh.
    - Verify that the uploaded logo appears in the Sidebar and Header.
3.  **Role Check**:
    - Login as an Agent or Client of the same company.
    - Verify that they see the same branding (white-labeling).
