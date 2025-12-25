# Walkthrough: Interactive Agent Workflow & Policy-Specific Data Integration

I have successfully implemented the interactive "Validate/Modify" workflow for AI Agents, with a specific focus on the Quote process and policy-specific client data.

## 1. Redesigned Quote Preview
The Quote Preview now features a dual-card vertical layout:
- **Quote Details (Top)**: Displays core information including the 3 new fields:
    - **Vehicle Mileage**
    - **Vehicle Registration Number**
    - **Driver's Driving Licence Number**
- **Premium Breakdown (Bottom)**: Displays the calculation logic with visual cues for Risk Adjustments (Red) and Discounts (Green).

## 2. Stateful Conversational Logic
The `QuoteAgentExecutor` now systematically collects information:
- **One-by-One Questioning**: If data is missing (e.g., mileage), the agent will ask specifically for it before generating the quote.
- **Database Lookup**: The agent automatically attempts to retrieve existing data from the `Client` and `ClientAutomobile` (or other policy-specific) tables if the user is identified, prepopulating the fields.

## 3. Policy-Specific Client Tables
I've implemented a robust database schema to store extended client details:
- **`client_automobile`**: Stores vehicle-specific data (mileage, registration, etc.).
- **`client_housing`**, **`client_health`**, **`client_travel`**, **`client_life`**: Dedicated tables for each policy type.

## 4. Enhanced Persistence Flow
When a user clicks **"Validate"** in the UI:
1. The `Quote` record is created in the database.
2. The policy-specific details provided during the chat are automatically **upserted** into the corresponding detail table (e.g., updating the client's vehicle mileage and registration number).

## 5. Quote Selection for Policy Creation
When you ask the AI to "create a policy", it now:
- **Queries Draft Quotes**: Fetches all quotes with status `draft`, `accepted`, or `sent`.
- **Displays a Selection Table**: Shows a dataset in the Preview area with creation date, quote number, client name, and type.
- **Convert Action**: Provides a "Convert to Policy" button for each row. Clicking it immediately initiates the conversion flow in the chat.

## Verification Steps
1. **Initiate Quote**: Ask the AI to "Create an automobile insurance quote for John Doe".
2. **Follow-up**: Observe the agent asking for missing fields like Mileage or License # one by one.
3. **Modify**: Click "Modify" and update a field (e.g., "update mileage to 20000").
4. **Validate**: Click "Validate" and verify data storage.
5. **Create Policy**: Say "create a policy".
6. **Select Quote**: Observe the "Select Quote to Convert" table in the right panel. Click "Convert to Policy" on one of the rows.
7. **Finalize**: Verify the policy is created and a new policy number is generated.

### Data Model Reference
- [client_details.py](file:///c:/Users/user/Desktop/Insurance%20SaaS/backend/app/models/client_details.py)
- [validation.py](file:///c:/Users/user/Desktop/Insurance%20SaaS/backend/app/api/v1/endpoints/validation.py)
- [quote-selection-preview.tsx](file:///c:/Users/user/Desktop/Insurance%20SaaS/frontend/components/ai-agent/previews/quote-selection-preview.tsx)
