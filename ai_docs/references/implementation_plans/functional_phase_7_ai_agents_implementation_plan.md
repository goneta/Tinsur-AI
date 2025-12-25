# Implementation Plan: Functional Phase 7 AI Agents

Transform the current stub AI agents for Phase 7 modules into functional agents by implementing ADK Tools that interact with the PostgreSQL database.

## Proposed Changes

### [Component] Loyalty Agent
Implement tools to query and managed loyalty points.

#### [NEW] [tools.py](file:///c:/Users/user/Desktop/Insurance%20SaaS/backend/agents/a2a_loyalty_agent/tools.py)
- `get_loyalty_points(client_id: str)`: Returns current balance, tier, and history.
- `redeem_loyalty_points(client_id: str, points: int)`: Deducts points and records redemption.

#### [MODIFY] [agent_executor.py](file:///c:/Users/user/Desktop/Insurance%20SaaS/backend/agents/a2a_loyalty_agent/agent_executor.py)
- Import tools from `tools.py`.
- Register tools in the `Agent` configuration.
- Update `execute` to use `self.agent.run(user_input)` with appropriate instructions containing the current `client_id`.

---

### [Component] Referrals Agent
Implement tools for referral code management and tracking.

#### [NEW] [tools.py](file:///c:/Users/user/Desktop/Insurance%20SaaS/backend/agents/a2a_referrals_agent/tools.py)
- `get_referral_info(client_id: str)`: Returns referral code and number of successful referrals.
- `create_referral_link(client_id: str)`: Generates a new unique referral code if one doesn't exist.

#### [MODIFY] [agent_executor.py](file:///c:/Users/user/Desktop/Insurance%20SaaS/backend/agents/a2a_referrals_agent/agent_executor.py)
- Integrate tools and update execution logic similar to Loyalty Agent.

---

### [Component] Tickets Agent
Implement tools for support ticket lifecycle management.

#### [NEW] [tools.py](file:///c:/Users/user/Desktop/Insurance%20SaaS/backend/agents/a2a_tickets_agent/tools.py)
- `create_support_ticket(client_id: str, subject: str, description: str, category: str, priority: str)`: Creates a new ticket in the DB.
- `get_ticket_status(ticket_number: str)`: Queries the status of a specific ticket.
- `list_active_tickets(client_id: str)`: Lists all open tickets for the client.

#### [MODIFY] [agent_executor.py](file:///c:/Users/user/Desktop/Insurance%20SaaS/backend/agents/a2a_tickets_agent/agent_executor.py)
- Replace manual DB logic with tools to allow the LLM to handle nuanced user requests more flexibly.

---

### [Component] Telematics Agent
Implement tools for usage-based insurance data retrieval.

#### [NEW] [tools.py](file:///c:/Users/user/Desktop/Insurance%20SaaS/backend/agents/a2a_telematics_agent/tools.py)
- `get_driving_stats(policy_id: str)`: Returns recent trip data, total distance, and safety score.
- `get_safety_recommendations(policy_id: str)`: Analyzes telematics data (harsh braking, etc.) and provides feedback.

#### [MODIFY] [agent_executor.py](file:///c:/Users/user/Desktop/Insurance%20SaaS/backend/agents/a2a_telematics_agent/agent_executor.py)
- Integrate tools and update execution logic.

---

### [Component] ML Agent
Implement tools for model metadata and insights.

#### [NEW] [tools.py](file:///c:/Users/user/Desktop/Insurance%20SaaS/backend/agents/a2a_ml_agent/tools.py)
- `list_active_models()`: Lists all deployed ML models and their accuracy.
- `get_model_insight(model_name: str)`: Returns specific details about a model's performance.

#### [MODIFY] [agent_executor.py](file:///c:/Users/user/Desktop/Insurance%20SaaS/backend/agents/a2a_ml_agent/agent_executor.py)
- Integrate tools and update execution logic.

---

## Verification Plan

### Automated Tests
- Create a test script `backend/tests/test_phase7_agents_functional.py` that mocks the ADK Agent but verifies the Tool functions against a test database.
- Run `pytest` on individual agent tools.

### Manual Verification
- Start the Agent Mesh.
- Use the Dashboard Chat to ask:
    - "How many loyalty points do I have?"
    - "Check the status of ticket TKT-12345"
    - "Give me my referral code"
    - "Show me my driving safety score for the last week"
    - "What is the accuracy of our current fraud detection model?"
