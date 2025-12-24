# Implementation Plan: Employee Profile Redesign

The objective is to transform the Employee Profile Page into a comprehensive dashboard featuring detailed info cards, performance statistics, and advanced filtering.

## User Review Required
> [!IMPORTANT]
> This plan assumes we will mock the "Education", "Communication", and specific "Performance Stats" data (Counts for Clients, Quotes, Policies, Claims) for now, as the current backend schema primarily stores account and basic profile info. We will create the UI structure to be ready for real data integration.

## Proposed Changes

### 1. New & Updated Components [MODIFY]
- **`EmployeeInfoCard`**: (Replacing `DetailsCard`, `PositionCard`, `EducationCard`)
    - **Header**: Contains the Profile Picture (Editable via `ProfileUploader`) in the top-right corner.
    - **Section 1 (Details)**: Full name, Phone number, Address.
    - **Section 2 (Position)**: Role, Job type, Salary, POS location.
    - **Section 3 (Education)**: List of Degrees, Diplomas, Certificates (Mock Data).
- **`EmployeePerformanceStats`**: (No change) A horizontal stats bar with tabs:
    - **Clients (10)**, **Quotes (8)**, **Policies (7)**, **Claims (3)**
- **`AdvancedFilter`**: A single filter system for Day, Week, Month, Year.
- **`PayrollCard`**: Displays Number of payslips, Paid salaries, Unpaid salaries.
- **`CommunicationCard`**: Displays Message/Document stats.

### 2. Page Refactor [MODIFY]
- **`frontend/app/dashboard/employees/[id]/page.tsx`**: 
    - Replace the existing `EmployeeProfile` usage with the new grid layout.
    - Implement the `AdvancedFilter` state lifting to filter the performance lists and charts.
    - Each tab in Performance Stats will use the same reusable `Card/List View` (DataView).

### 3. Visuals
- Dynamic charts for each tab in the Performance Stats section.
- Consistency with existing Client and Employee list and card views.

## Verification Plan

### Automated Tests
- None planned for this UI refactor.

### Manual Verification
1.  **Navigate to Employee Profile**: Click "Eye" icon on an Employee card in the dashboard.
2.  **Verify Cards**: Check that all requested cards (Details, Position, Education, Payroll, Communication) are displayed with correct/mock data.
3.  **Verify Performance Tabs**: 
    - Click through the Clients, Quotes, Policies, and Claims tabs.
    - Ensure the list/card view toggle and search work for each list.
4.  **Verify Advanced Filter**: 
    - Apply filters by Day, Week, Month, and Year.
    - Verify that the counts and charts update dynamically.
5.  **Responsiveness**: Verify the layout behaves well on different screen sizes.
