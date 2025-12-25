# Implementation Plan - AI Subscription & Quota System

This plan outlines the changes required to implement a three-tier subscription system to manage AI usage and resolve quota issues.

## Proposed Changes

### [Component] Backend Models & Database
#### [MODIFY] [company.py](file:///c:/Users/user/Desktop/Insurance%20SaaS/backend/app/models/company.py)
- [x] Add `ai_plan` column (BASIC, BYOK, CREDIT).
- [x] Add `ai_api_key_encrypted` column for tenant-provided keys (BYOK Plan).
- [x] Add `ai_credits_balance` column for credit tracking (CREDIT Plan).

#### [NEW] [system_settings.py](file:///c:/Users/user/Desktop/Insurance%20SaaS/backend/app/models/system_settings.py)
- Create a `SystemSettings` table to store Global AI API keys (Google, Claude, OpenAI) and global defaults.
- This replaces the need to manually edit `.env` for the SaaS owner and allows instant updates across all agents without restarts.

---

### [Component] AI Agent Mesh Enhancements
#### [MODIFY] [agent_client.py](file:///c:/Users/user/Desktop/Insurance%20SaaS/backend/app/core/agent_client.py)
- Implement **API Key Hierarchy Logic**:
    1. Check for Company BYOK key.
    2. Check for Super Admin Global key (from `SystemSettings`).
    3. Fallback to `.env` (Legacy support to ensure nothing breaks).
- Pass the resolved key in the request context to specialist agents.

#### [MODIFY] [agents/__init__.py](file:///c:/Users/user/Desktop/Insurance%20SaaS/backend/google/adk/agents/__init__.py)
- Update `Agent.run` to prioritize the API key passed in the request.
- Ensure `genai.configure(api_key=...)` is scoped correctly for the request.

---

### [Component] API Endpoints
#### [MODIFY] [chat.py](file:///c:/Users/user/Desktop/Insurance%20SaaS/backend/app/api/v1/endpoints/chat.py)
- Handle "Insufficient Credits" exceptions and return a specific error code.

#### [NEW] [subscription.py](file:///c:/Users/user/Desktop/Insurance%20SaaS/backend/app/api/v1/endpoints/subscription.py)
- Endpoints to update plans, set API keys, and check credit balance.

---

### [Component] Frontend UI
#### [NEW] [SuperAdminAISettings.tsx](file:///c:/Users/user/Desktop/Insurance%20SaaS/frontend/components/admin/SuperAdminAISettings.tsx)
- Panel for the SaaS owner to configure global API keys and manage default credit pricing.

#### [NEW] [CompanyAISettings.tsx](file:///c:/Users/user/Desktop/Insurance%20SaaS/frontend/components/settings/CompanyAISettings.tsx)
- UI for company admins to choose a plan and provide a custom API key if on the BYOK tier.

#### [NEW] [CreditLimitModal.tsx](file:///c:/Users/user/Desktop/Insurance%20SaaS/frontend/components/ai-agent/CreditLimitModal.tsx)
- Modal to prompt users to buy credits when exhausted.

---

### [Component] Testing & Development Utilities
#### [MODIFY] [dev.py](file:///c:/Users/user/Desktop/Insurance%20SaaS/backend/app/api/v1/endpoints/dev.py)
- [ ] Add `seed_ai_test_users` endpoint to create pre-configured users for each AI plan tier.
- [ ] Add `topup_credits_dev` endpoint to allow instant credit addition without payment during testing.

#### [MODIFY] [AiSubscriptionSettings.tsx](file:///c:/Users/user/Desktop/Insurance%20SaaS/frontend/components/settings/ai-subscription-settings.tsx)
- [ ] Add a "Dev: Top up $10" button visible only in development mode.

## Verification Plan
### Automated Tests
- Test that Plan 1 (BASIC) blocks AI requests.
- Test that Plan 2 (BYOK) uses the company-provided key.
- Test that Plan 3 (CREDIT) deducts credits and blocks when zero.

### Manual Verification
- Run `POST /dev/seed-ai-test-users` and verify login for all 4 test accounts.
- Verify the credit modal appears in the dashboard when credits are 0.
- Verify the settings page correctly updates company AI settings.
- Test the "Dev: Top up" button in the settings page.
