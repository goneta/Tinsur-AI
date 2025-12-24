# Plan: Interactive Validate/Modify Workflow for AI Agents

Enable a multi-step verification and modification flow for all AI-generated entities (Quotes, Policies, Claims). This allows users to review drafts, modify individual elements via chat interface, and persist the final version to the database.

## User Review Required

> [!IMPORTANT]
> This change introduces a new "Interaction Mode" in the chat interface. Agents will now return structured field lists that require user input to proceed.

## Database Schema Updates (New Tables)

Create policy-specific tables to store detailed client information:
- **`client_automobile`**: `id`, `client_id`, `vehicle_value`, `vehicle_age`, `vehicle_mileage`, `vehicle_registration`, `driver_dob`, `license_number`.
- **`client_house`**: Related fields for Housing.
- **`client_health`**: Related fields for Health.
- **`client_travel`**: Related fields for Travel.
- **`client_life`**: Related fields for Life.

## Proposed Changes

### Interaction Protocol
Standardize a JSON-based protocol for the "Modify" state. The agent must ensure the following fields are collected (asking one-by-one if missing):
- **Core**: Client Name, Policy Type (e.g. Automobile), Duration (months), Payment Frequency, Manual Discount.
- **Auto-specific**: Coverage Amount, Vehicle Value, Vehicle Age (year), Driver Date of Birth, **Vehicle Mileage**, **Vehicle Registration Number**, **Driver Licence Number**.

Example Protocol:
```json
{
  "interaction": {
    "type": "modify",
    "entity": "quote",
    "fields": [
      {"label": "Client Name", "key": "client_name", "value": "Valued Client"},
      {"label": "Policy Type", "key": "policy_type", "value": "Automobile"},
      {"label": "Coverage Amount", "key": "coverage_amount", "value": 5000000},
      {"label": "Duration (Months)", "key": "duration_months", "value": 12},
      {"label": "Payment Frequency", "key": "payment_frequency", "value": "Monthly"},
      {"label": "Vehicle Value", "key": "vehicle_value", "value": 25000000},
      {"label": "Vehicle Age", "key": "vehicle_age", "value": 2022},
      {"label": "Driver DOB", "key": "driver_dob", "value": "1990-01-01"},
      {"label": "Vehicle Mileage", "key": "vehicle_mileage", "value": 15000},
      {"label": "Registration #", "key": "vehicle_registration", "value": "ABC-123"},
      {"label": "License #", "key": "license_number", "value": "LIC-98765"},
      {"label": "Manual Discount", "key": "manual_discount", "value": 0}
    ]
  }
}
```

### Quote Selection Protocol
When a user asks to "create a policy", the agent returns a dataset of draft quotes for selection.
```json
{
  "type": "quote_selection",
  "data": {
    "quotes": [
      {
        "id": "...",
        "quote_number": "Q-ABCD",
        "client_name": "John Doe",
        "policy_type": "Automobile",
        "created_at": "2023-11-01"
      }
    ]
  }
}
```

### Backend Implementation

#### [NEW] [validation.py](file:///c:/Users/user/Desktop/Insurance%20SaaS/backend/app/api/v1/endpoints/validation.py)
- `POST /api/v1/validation/validate`: 
    - Receives entity data.
    - Persists basic `Quote` record.
    - **New**: Upserts data into the corresponding `client_[policy_type]` table (e.g. `client_automobile`).

#### [MODIFY] [agent_executor.py](file:///c:/Users/user/Desktop/Insurance%20SaaS/backend/agents/a2a_quote_agent/agent_executor.py) (and others)
- Implement stateful logic to check for missing required fields.
- If fields are missing, the agent asks for them **one by one** in the chat.
- Implement logic to handle "Modify Draft" and individual "Edit [Field]" commands.
- Respond with the structured `interaction` JSON when requested.

---

### Frontend Implementation

#### [MODIFY] [quote-preview.tsx](file:///c:/Users/user/Desktop/Insurance%20SaaS/frontend/components/ai-agent/previews/quote-preview.tsx)
- Redesign the layout to follow the reference image:
    - **Top Card**: "Quote Details" (Number, Status Badge, Policy Type, Validity Date).
    - **Bottom Card**: "Premium Breakdown" (Coverage, Base Premium, Risk Adjustment in Red, Discount in Green, Final Premium in Bold).
- Add "Validate Quote" and "Modify Quote" buttons at the bottom.
- Add prop `onAction` to bubble up clicks to the parent.

#### [NEW] [quote-selection-preview.tsx](file:///c:/Users/user/Desktop/Insurance%20SaaS/frontend/components/ai-agent/previews/quote-selection-preview.tsx)
- Render a table/dataset of quotes.
- Each row includes a "Convert to Policy" button.
- Button triggers an `onAction` with `type: 'convert_to_policy', data: { quote_id: '...' }`.

#### [MODIFY] [right-panel.tsx](file:///c:/Users/user/Desktop/Insurance%20SaaS/frontend/components/ai-agent/right-panel.tsx)
- Add case for `quote_selection`.
- Add detection for `interaction` JSON in `parsePreviewData`.
- Implement a custom renderer for `ChatMessage` that displays the "Edit/Keep" list when `interaction.type === 'modify'`.
- Manage state for the current field being edited.

#### [MODIFY] [left-panel.tsx](file:///c:/Users/user/Desktop/Insurance%20SaaS/frontend/components/ai-agent/left-panel.tsx)
- Add detection for `interaction` JSON in `parsePreviewData`.
- Implement a custom renderer for `ChatMessage` that displays the "Edit/Keep" list when `interaction.type === 'modify'`.
- Manage state for the current field being edited.

#### [MODIFY] [ai-api.ts](file:///c:/Users/user/Desktop/Insurance%20SaaS/frontend/lib/ai-api.ts)
- Add the `validateEntity` method to call the new backend endpoint.

---

## Verification Plan

### Automated Tests
- Run `pytest` on the new `validation` endpoint.
- Mock agent responses with `interaction` JSON to verify frontend rendering logic.

### Manual Verification
1.  **Generate Quote**: Ask the agent for a quote.
2.  **Preview Review**: Verify "Validate" and "Modify" buttons appear in the right panel.
3.  **Initiate Modify**: Click "Modify Quote".
4.  **Edit Flow**: 
    - Verify the chat displays the element list with "Edit/Keep".
    - Click "Edit" for "Client Name".
    - Type a new name in the chat box.
    - Verify the preview updates immediately without full redraw.
5.  **Final Validation**: Click "Validate Quote" and verify it's saved in the database (refresh the portal dashboard to see it).
