# Redesign Employee Profile Page

The objective is to transform the Employee Profile Page into a comprehensive dashboard featuring detailed info cards, performance statistics, and advanced filtering.

## User Review Required
> [!IMPORTANT]
> This plan assumes we will mock the "Education", "Communication", and specific "Performance Stats" data for now, as the current backend schema likely does not support these detailed fields. We will create the UI structure to be ready for real data integration.

## Proposed Changes

### 1. New Components [NEW]
- **`EmployeeDetailsCard`**: Displays basic info (Name, Phone, Address).
- **`EmployeePositionCard`**: Displays Role, Job, Salary, Location.
- **`EmployeeEducationCard`**: Displays Degrees, Diplomas (Mock Data).
- **`EmployeeStatsTabs`**: A tabbed container for Clients, Quotes, Policies, Claims.
- **`StatsList`**: A wrapper around `DataView` to display the simple lists for each tab.
- **`PerformanceChart`**: A dynamic chart component (using Recharts) for the stats tabs.
- **`AdvancedFilter`**: A global filter component (Day, Week, Month, Year).
- **`PayrollStatsCard`**: Displays Payslips, Paid, Unpaid counts.
- **`CommunicationStatsCard`**: Displays Messages/Docs stats.

### 2. Page Refactor [MODIFY]
- **`frontend/app/dashboard/employees/[id]/page.tsx`**: 
    - Replace the existing `EmployeeProfile` usage with the new grid layout.
    - Implement the `AdvancedFilter` state lifting.
    - Fetch (or mock) the necessary data for each card.

### 3. Data Integration
- **Clients Tab**: Use `clientsApi.getClients` filtered by `created_by` (if available) or filter client-side.
- **Quotes/Policies/Claims Tabs**: Similar fetching logic.
- **Mock Data**: For Education and Communication stats, we will hardcode valid-looking data structures to demonstrate the UI.

## Verification Plan

### Automated Tests
- None planned for this UI refactor.

### Manual Verification
1.  **Navigate to Employee Profile**: Click "Eye" icon on Employee card.
2.  **Verify Cards**: Check Details, Position, Education, Payroll, Communication cards appear with data.
3.  **Verify Tabs**: Click Clients/Quotes/Policies/Claims tabs. Ensure list updates.
4.  **Verify Filter**: Change Year/Month in Advanced Filter. Verify Chart updates (visually).
5.  **Responsiveness**: Check layout on mobile vs desktop.
