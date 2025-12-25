# Phase 5: Payroll & HR Implementation Plan

## Goal Description
Implement the Payroll & HR module (Governance and compliance) to manage employees and their payroll. This includes:
1.  **Employee Management**: Add/Edit employees, assign roles (Admin, Manager, Agent, Receptionist).
2.  **Payroll System**: Manage employee payment details (Mobile Money: Orange, MTN, Wave, Moov; Bank Transfer). Record payroll transactions.

## Proposed Changes

### Backend

#### [NEW] [employee.py](file:///c:/Users/user/Desktop/Insurance%20SaaS/backend/app/models/employee.py)
Create `EmployeeProfile` model to store extended employee details (Payroll info).
- `id`: UUID
- `user_id`: UUID (FK to users.id)
- `payment_method`: String (mobile_money, bank_transfer)
- `mobile_money_provider`: String (orange, mtn, wave, moov) - optional
- `mobile_money_number`: String - optional
- `bank_name`: String - optional
- `bank_account_number`: String - optional
- `salary`: Numeric - optional (base salary)

#### [NEW] [payroll.py](file:///c:/Users/user/Desktop/Insurance%20SaaS/backend/app/models/payroll.py)
Create `PayrollTransaction` model.
- `id`: UUID
- `employee_id`: UUID (FK to users.id)
- `amount`: Numeric
- `payment_date`: DateTime
- `payment_method`: String
- `status`: String (pending, paid, failed)
- `description`: String (e.g., "December Salary")

#### [MODIFY] [backend/app/models/__init__.py](file:///c:/Users/user/Desktop/Insurance%20SaaS/backend/app/models/__init__.py)
- Import and register new models.

#### [NEW] [backend/app/schemas/employee.py](file:///c:/Users/user/Desktop/Insurance%20SaaS/backend/app/schemas/employee.py)
- `EmployeeCreate`: Extends UserCreate, includes role and profile fields.
- `EmployeeUpdate`: For updating details.
- `EmployeeResponse`: Combined User + Profile data.
- `PayrollTransactionCreate`: Schema for processing a payment.
- `PayrollTransactionResponse`: Schema for reading.

#### [NEW] [backend/app/api/v1/endpoints/employees.py](file:///c:/Users/user/Desktop/Insurance%20SaaS/backend/app/api/v1/endpoints/employees.py)
- `GET /employees`: List employees (users with employee roles).
- `POST /employees`: Create new employee (creates User + EmployeeProfile).
- `GET /employees/{id}`: Get details.
- `PUT /employees/{id}`: Update.

#### [NEW] [backend/app/api/v1/endpoints/payroll.py](file:///c:/Users/user/Desktop/Insurance%20SaaS/backend/app/api/v1/endpoints/payroll.py)
- `POST /payroll`: Record a payroll payment.
- `GET /payroll`: List transactions.

#### [MODIFY] [backend/app/api/v1/router.py](file:///c:/Users/user/Desktop/Insurance%20SaaS/backend/app/api/v1/router.py)
- Include new routers.

### Frontend

#### [NEW] [app/dashboard/employees/page.tsx](file:///c:/Users/user/Desktop/Insurance%20SaaS/frontend/app/dashboard/employees/page.tsx)
- Main employee management dashboard.
- List view of employees.
- "Add Employee" button opening a modal/drawer.

#### [NEW] [app/dashboard/employees/components/EmployeeForm.tsx](file:///c:/Users/user/Desktop/Insurance%20SaaS/frontend/app/dashboard/employees/components/EmployeeForm.tsx)
- Form to add/edit employee (Personal info, Role, Payment details).

#### [NEW] [app/dashboard/payroll/page.tsx](file:///c:/Users/user/Desktop/Insurance%20SaaS/frontend/app/dashboard/payroll/page.tsx)
- Payroll processing interface.
- Select employee -> Enter amount -> Confirm payment.
- History table.

## Verification Plan

### Automated Tests
- No existing tests found for this module (it's new).
- Will verify manually via the UI and API calls.

### Manual Verification
1.  **Frontend**:
    - Navigate to `/dashboard/employees`.
    - Click "Add Employee".
    - Fill form:
        - Information: Test Name, email.
        - Role: Select "Manager".
        - Payment: Select "Mobile Money", Provider "Orange", Number "07...".
    - Submit.
    - Verify employee appears in list.
    - Navigate to `/dashboard/payroll`.
    - Select the new employee.
    - Process a payment.
    - Verify transaction appears in history.
2.  **API Verification**:
    - Use Swagger UI (`/docs`) to call `GET /api/v1/employees` and confirm structure.
