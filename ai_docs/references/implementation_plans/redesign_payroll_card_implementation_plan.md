# Redesign Payroll Card and Add Features

Redesign the Payroll page to align with the Employee list page aesthetic, adding filtering, searching, and a view toggle (Card/List). Ensure employee profile pictures are used and shared across components.

## Proposed Changes

### [Component Name] Payroll Module

#### [MODIFY] [page.tsx](file:///c:/Users/user/Desktop/Insurance%20SaaS/frontend/app/dashboard/payroll/page.tsx)
- Add state for `viewMode` ('card' | 'list'), `searchTerm`, and `filterField`.
- Implement filtering logic for the employees list.
- Add Search and Filter UI (Select and Input) above the employee cards.
- Add View Toggle (Card/List) button group.
- Update Card view:
    - Change layout to match Employee card (from reference image).
    - Use `Avatar` with `getProfileImageUrl(employee.profile_picture)`.
    - Display Employee Name, Email, Role, Job Title, and Department.
    - Keep "Pay Now" button functionality.
- Implement List view using `DataTable` component.

#### [NEW] [columns.tsx](file:///c:/Users/user/Desktop/Insurance%20SaaS/frontend/app/dashboard/payroll/columns.tsx)
- Define columns for the Payroll `DataTable`:
    - Employee (Photo + Name)
    - Email
    - Role
    - Salary (formatted)
    - Payment Method
    - Actions (Pay Now button)

## Verification Plan

### Manual Verification
1.  **Navigate to Payroll page**:
    - Verify that the search bar and filter dropdown are present.
    - Verify that the View Toggle (Card/List) is present.
2.  **Test Filtering/Searching**:
    - Enter a name in the search bar and verify that the list/cards update.
    - Change the filter field (Name, Email, etc.) and verify search works correctly.
3.  **Test View Toggle**:
    - Click "List" and verify the data table appears with sortable columns.
    - Click "Card" and verify the card view appears with the new design.
4.  **Verify Employee Photos**:
    - Ensure employee profile pictures are displayed in both Card and List views.
    - Verify that the image is the same as the one on the Employee list page.
5.  **Test "Pay Now" functionality**:
    - Click "Pay Now" in both Card and List views and verify the payment dialog opens correctly.
