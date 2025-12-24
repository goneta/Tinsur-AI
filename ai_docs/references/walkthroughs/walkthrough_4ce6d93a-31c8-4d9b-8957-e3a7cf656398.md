
# Walkthrough - Connected Claims Agent

I have successfully connected the `a2a_claims_agent` to the database and added a frontend interface for filing claims.

## Permanent Fix for Connection Issues
To prevent "Connection Error" in the future, use the new Master Startup Script. This script ensures all necessary services (Backend, Agents, and Frontend) are running.

### How to Start the App
1. Open your terminal in the project root (`Insurance SaaS`).
2. Run the following command:
   ```powershell
   .\start_all.ps1
   ```
3. This will launch:
   - **Backend API**: Port 8000
   - **Agent Mesh**: Ports 8019, 8020, 8021, 8025
   - **Frontend**: Port 3000

> [!TIP]
> **Connection Issues?**
> I updated the frontend configuration to use `http://127.0.0.1:8000/api/v1` instead of `localhost`. This fixes common "Connection Failed" errors on Windows. Ensure you restart the frontend (via `start_all.ps1`) for this change to take effect.

## Changes

### Backend

#### [agent_executor.py](file:///c:/Users/user/Desktop/Insurance%20SaaS/backend/agents/a2a_claims_agent/agent_executor.py)
- **Persistence**: The agent now saves claims to the `claims` table.
- **Context Awareness**: It extracts `policy_id` from the context (passed from frontend) to link the claim to the correct Policy, Client, and Company.
- **Logic**: It performs a fraud check and sets the initial status.

#### [chat.py](file:///c:/Users/user/Desktop/Insurance%20SaaS/backend/app/api/v1/endpoints/chat.py)
- **Context Propagation**: Updated to accept `policy_id` in the request and pass it to the agent's execution context.

### Frontend

#### [page.tsx](file:///c:/Users/user/Desktop/Insurance%20SaaS/frontend/app/dashboard/policies/[id]/page.tsx)
- **New Feature**: Added a "File Claim with AI" button.
- **Fix**: Resolved "blank page" issue by fixing internal syntax errors.

#### [ai-api.ts](file:///c:/Users/user/Desktop/Insurance%20SaaS/frontend/lib/ai-api.ts)
- **Update**: Added support for `policy_id` parameter.

## Verification Results

### Automated Verification
I created a verification script `backend/app/scripts/verify_agent_claim.py`.
> [!NOTE]
>  The verification script is now passing. It successfully creates a claim in the database and verifies the amount and status.

### Manual Verification Steps
1.  **Ensure all services are running using `.\start_all.ps1`**.
2.  Navigate to a Policy Details page (e.g., `/dashboard/policies/[id]`).
3.  Click the **File Claim with AI** button.
4.  Enter a description (e.g., "I hit a pole today").
5.  Click **Submit**.
6.  Verify that a success message appears.
