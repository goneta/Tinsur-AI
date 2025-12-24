# Implementation Plan: Comprehensive Client Management System

This plan outlines the implementation of a full-featured Client Management System capable of handling detailed information for all insurance types (Automobile, Property, Health, Life).

## User Review Required

> [!IMPORTANT]
> This is a significant schema expansion. New tables and columns will be added. Existing client data will remain valid, but will be "incomplete" according to the new schema until updated.

## Proposed Changes

### Database Schema & Models

#### [MODIFY] [client.py](file:///C:/Users/user/Desktop/Insurance%20SaaS/backend/app/models/client.py)
- Update `Client` model to include:
    - **Identity**: `nationality`, `id_expiry_date`, `marital_status`.
    - **Compliance**: `kyc_status`, `pep_status`, `consent_accepted`.
    - **Professional**: `occupation`, `employer`, `employment_status`, `annual_income`.

#### [MODIFY] [client_details.py](file:///C:/Users/user/Desktop/Insurance%20SaaS/backend/app/models/client_details.py)
- **`ClientAutomobile`**: Add make, model, year, VIN, usage, driving history, etc.
- **`ClientHousing`**: Add property type, occupancy, risks, ownership details, etc.
- **`ClientHealth`**: Add height, weight, medical history, family history, etc.
- **`ClientLife`**: Add dependents, lifestyle risks, beneficiaries, etc.

### Pydantic Schemas

#### [MODIFY] [client.py](file:///C:/Users/user/Desktop/Insurance%20SaaS/backend/app/schemas/client.py)
- Update `ClientBase/Create/Update` to include all new core fields.
- Create new schemas for sub-types (or put them in a new `client_details.py` schema file):
    - `ClientAutomobileCreate`, `ClientAutomobileUpdate`
    - `ClientHousingCreate`, `ClientHousingUpdate`
    - `ClientHealthCreate`, `ClientHealthUpdate`
    - `ClientLifeCreate`, `ClientLifeUpdate`

### Backend API

#### [MODIFY] [clients.py](file:///C:/Users/user/Desktop/Insurance%20SaaS/backend/app/api/v1/endpoints/clients.py)
- Update `create_client` and `update_client` to handle extended core fields.
- Add new endpoints for managing specific details:
    - `PUT /clients/{id}/automobile`
    - `PUT /clients/{id}/housing`
    - `PUT /clients/{id}/health`
    - `PUT /clients/{id}/life`
    - `GET /clients/{id}/full-profile`: Retrieve all associated details.

### Frontend Implementation

#### [NEW] [Client Management Pages](file:///C:/Users/user/Desktop/Insurance%20SaaS/frontend/app/dashboard/clients)
- `page.tsx`: List of clients with advanced filters.
- `new/page.tsx`: Multi-step form to create a new client.
- `[id]/page.tsx`: Comprehensive Detail View with tabs:
    - **Profile**: Core details.
    - **Automobile**: Vehicle & Driving history.
    - **Property**: Real estate details.
    - **Health**: Medical data.
    - **Life**: Beneficiaries & Lifestyle.

#### [NEW] [Client Service](file:///C:/Users/user/Desktop/Insurance%20SaaS/frontend/lib/client-api.ts)
- Implement `clientApi` to handle all new endpoints.

## Verification Plan

### Automated Tests
- Create `backend/tests/api/test_client_full.py`:
    - Test creating a client with all core fields.
    - Test adding/updating Automobile details.
    - Test adding/updating Housing details.
    - Test adding/updating Health details.
    - Test adding/updating Life details.

### Manual Verification
1. Navigate to "Clients" tab in Dashboard.
2. Click "New Client" and fill out the "Common Details" form.
3. Save and go to valid detail page.
4. Switch to "Automobile" tab, enter vehicle info, save, verify persistence.
5. Create a Policy and verify user can select this client and data is available.
