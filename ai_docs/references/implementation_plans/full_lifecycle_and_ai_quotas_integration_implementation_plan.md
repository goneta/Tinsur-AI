# Implementation Plan - Phase 10.5: AI Refinements

Enhance the AI Subscription and Quota system with better visibility for users and admins.

## Proposed Changes

### Backend

#### [MODIFY] [subscription.py](file:///c:/Users/user/Desktop/Insurance%20SaaS/backend/app/api/v1/endpoints/subscription.py)
- Add a new endpoint `GET /usage/stats` to retrieve AI usage aggregated by day for the last 30 days.

### Frontend

#### [MODIFY] [agent-workspace.tsx](file:///c:/Users/user/Desktop/Insurance%20SaaS/frontend/components/ai-agent/agent-workspace.tsx)
- Integrate a `CreditsBadge` in the header section of the AI Agent Manager.
- Fetch current credit balance and plan type to determine if the badge should be shown (only for `CREDIT` plan).

#### [MODIFY] [ai-subscription-settings.tsx](file:///c:/Users/user/Desktop/Insurance%20SaaS/frontend/components/settings/ai-subscription-settings.tsx)
- Add a "Usage Over Time" section.
- Implement a Bar Chart using Recharts to visualize the last 30 days of AI consumption.
- Show "Top Agents" or "Usage by Action" if data allows.

## Verification Plan

### Automated Tests
- Run `test_ai_quotas.py` to ensure core logic is still intact.
- (Optional) Add a new test for the usage stats endpoint.

### Manual Verification
- Log in as a `company_admin` and check the Settings > AI tab for the new chart.
- Navigate to the AI Agent Manager and verify the Credits Badge is visible and accurate.
- Simulate an AI interaction and confirm the badge/chart updates (after refresh).
