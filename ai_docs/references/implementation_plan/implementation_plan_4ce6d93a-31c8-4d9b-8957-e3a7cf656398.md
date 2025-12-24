
# Implementation Plan - Connect Claims Agent to System

The goal is to make the `a2a_claims_agent` fully functional by connecting it to the database for persistence and adding a frontend entry point for users to interact with it.

## User Review Required

> [!IMPORTANT]
> This plan involves modifying the agent to write directly to the production database ("claims" table). Verify if this permission is acceptable for the agent.

## Proposed Changes

### Backend - Agent Persistence

#### [MODIFY] [agent_executor.py](file:///c:/Users/user/Desktop/Insurance%20SaaS/backend/agents/a2a_claims_agent/agent_executor.py)
- Import `Claim` model from `app.models.claim`.
- In `_process_claim`, instead of just returning a mock object:
    - Generate a unique `claim_number`.
    - Create a new `Claim` instance with data parsed from the request (description, amount, policy_id).
    - Commit the `Claim` to the database using `SessionLocal`.
    - Return the actual `claim.id` and status in the response.

### Frontend - User Interface

#### [MODIFY] [page.tsx](file:///c:/Users/user/Desktop/Insurance%20SaaS/frontend/app/dashboard/policies/[id]/page.tsx)
- Add a "File Claim with AI" button to the policy details page (next to "Make Payment").
- This button should likely trigger a chat interface or a modal that sends a message to the agent.
- For now, we can implement a simple prompt dialog or a direct API call to the agent if an endpoint exists.
- *Note*: Since the agent runs on a separate port (8019), we need to ensure the frontend can reach it, or use a proxy in the main backend.
    - *Decision*: We will route agent requests through a new endpoint in the main backend `POST /api/agent/claims` which forwards to the agent, OR use the existing agent client infrastructure if present.
    - *Assumption*: We will start by adding the button which just logs "Not implemented" if no agent client is ready, or use `claimApi.createClaim` if the user wants to do it manually, but the goal is *AI Agent* integration.
    - *Refined Plan*: We will add the button and a simple "Describe your claim" dialog. On submit, it calls the agent.

## Verification Plan

### Automated Tests
- Run `backend/agents/a2a_claims_agent/__main__.py` and send a test curl request to port 8019.
- Verify a new row is created in the `claims` table.

### Manual Verification
- Go to `http://localhost:3000/dashboard/policies/[id]`.
- Click "File Claim with AI".
- Enter a claim description (e.g., "I crashed my car").
- Verify the agent responds and a claim appears in the "Documents" or "Claims" section (if we add one).
