# Implementation Plan: API Key System Refinement & Portal Integration

This plan outlines the steps to finalize the API Key management system by implementing database-backed authentication, connecting the client portal to live data, and verifying the AI Agent's configuration (specifically Google API Key usage).

## Proposed Changes

### Backend Authentication

#### [MODIFY] [agent_auth.py](file:///c:/Users/user/Desktop/Insurance%20SaaS/backend/app/middleware/agent_auth.py)
Refactor the middleware to:
- Accept a database session.
- Hash the incoming `X-API-KEY`.
- Verify the hashed key against the `api_keys` table.
- Upate `last_used_at` timestamp on successful authentication.
- Fallback to the `A2A_INTERNAL_API_KEY` for internal service-to-service communication.

### Client Portal Dashboard

#### [MODIFY] [page.tsx](file:///c:/Users/user/Desktop/Insurance%20SaaS/frontend/app/portal/page.tsx)
- Replace hardcoded dashboard statistics with real data fetched from the backend.
- Create new backend endpoints if necessary to provide summary data (e.g., active policies count, pending payments).

### AI Agent Verification

#### [VERIFY] Google API Key Usage
- Confirm that `GOOGLE_API_KEY` is being passed correctly to the AI models (Gemini) in the agent executors.
- Fix issues in `LiteLlmAgentExecutor` where keys might be missing or defaulted incorrectly.

## Verification Plan

### Automated Tests
- Create a test script to generate an API key via the UI/API and then attempt to call an agent endpoint using that key.
- Verify that revoked keys (or invalid keys) return a 403 Forbidden error.

### Manual Verification
- Log in as a user and verify that the Client Portal shows real data (e.g., if there are 3 policies in the DB, it should show 3).
- Test creating and revoking API keys in the Settings -> API Keys page.
