## Master Plan — ADK-Based Multi‑Agent Banking App (Bake Off 2025)

### 1) Overview

- **Goal**: Ship a two‑pane, multi‑page banking app powered by ADK agents with A2A to the Cymbal Bank Agent. Left panes show structured snapshots; right panes are conversational assistants.
- **Core pattern**: Snapshot = two agents (DataAgent → FormatterAgent) to satisfy ADK `output_schema` constraint. Chat = one agent (tool‑enabled, streaming plaintext output).
- **MVP scope**: Fully implement Spending and Goals (both panes). Stub Debts & Investments, Partners & Offers, Advisors & Meetings with working shell UIs and endpoints that return simple placeholder content until agents are ready.

### 2) Assumptions

- **A2A (black box)**: The Cymbal Bank A2A Agent is treated as a black box with documented high‑level capabilities (e.g., “fetch spending history,” “summarize cashflow,” “list goals,” “update goal,” “list advisors,” “schedule meeting”). Our agents make capability‑based requests to this agent; we do not rely on or name its internal tools.
- **Permissions**: Single global "Enable Agents" gate controls access to data/APIs across the app. When disabled, feature pages show an enable prompt. DataAgents request read capabilities; write actions are only available when agents are enabled (granular toggles can be added later if time allows).
- **NextJS**: Two‑pane layout per page; backend API routes proxy to ADK orchestration.
- **Transport**: All API endpoints emit Server‑Sent Events (SSE). We stream ADK event JSON envelopes on `data:` lines; clients parse `content.parts` and `actions.stateDelta`. Snapshots stream progress envelopes and a final blocks payload; chat streams incremental text via `content.parts[].text` across frames.

---

### 3) NextJS Plan (high‑level app design per page)

#### 3.1 Shared UI/State

- **Layout**: Two columns: left Snapshot pane, right Chat pane. Shared header for navigation and permissions status.
- **Components**:
  - `EnableAgentsGate` — wraps pages; if agents disabled, shows CTA to enable and blocks calls.
  - `SnapshotRenderer` — renders `insight`, `chart`, `table` blocks.
  - `Chart` — simple primitives for bar/line/area using `ChartSpec` fields.
  - `DataTable` — columns/rows with basic sorting and truncation.
  - `ChatPane` — message list, input box; supports streaming over SSE/WebSocket for chat endpoints.
  - `ErrorBanner` — non‑blocking error notices.
- **State**:
  - AgentStatus: `enabled` boolean loaded at app start and cached; controls `EnableAgentsGate`.
  - Snapshot: loading/error/lastUpdated; cached per page.
  - Chat: in‑memory thread per page; optimistic send; cancel in‑flight; streaming buffer handling.

#### 3.2 Pages

- `Onboarding` (`/onboarding`)
  - **Purpose**: Establish A2A handshake and allow user to enable agents globally.
  - **UX**: Connect button → calls `POST /api/onboarding/connect-a2a`; then show single primary button “Enable Agents” → `POST /api/agent-status` with `{ enabled: true }`; continue to Spending.
  - **Empty/Errors**: If agents not enabled, feature pages render `EnableAgentsGate` prompt.

 - `Spending` (`/spending`)
  - **Goal**: Help users quickly see where money goes and identify practical savings opportunities.
  - **Left (Snapshot)**: On load, call `POST /api/spending-snapshot` (SSE). Shows: one-line insight, spend by category chart, monthly trend chart, and top merchants table for immediate context.
  - **Right (Chat)**: Sends to `POST /api/spending` (SSE). Turns insight into guidance: answer budget questions, highlight cutback areas, detect unused subscriptions, and propose next steps.
  - **User interaction**: Chat only (no manual controls beyond sending messages).

 - `Goals` (`/goals`)
  - **Goal**: Set and achieve savings goals with a realistic plan and clear progress.
  - **Left (Snapshot)**: `POST /api/goals-snapshot` (SSE). Shows: progress to target, timeline trend (if available), upcoming scheduled actions, and a one-line insight.
  - **Right (Chat)**: `POST /api/goals` (SSE). Designs a plan (how much per month), adjusts targets/dates, and sets reminders/schedules via capability-based actions.
  - **User interaction**: Chat only.

 - `Debts & Investments` (`/portfolio`)
  - **Goal**: Understand net worth, allocations, and choose a debt payoff strategy.
  - **Left (Snapshot)**: `POST /api/portfolio-snapshot` (SSE). Shows: net worth trend, allocation by asset class, liabilities table, plus an insight.
  - **Right (Chat)**: `POST /api/portfolio` (SSE). Explains trends, flags concentration risks, and recommends payoff order (e.g., avalanche vs snowball) based on the user’s profile.
  - **User interaction**: Chat only. MVP starts read-only; enrich as time permits.

 - `Perks` (`/perks`)
  - **Goal**: Maximize savings by discovering and applying the best perks/offers.
  - **Left (Snapshot)**: `POST /api/perks-snapshot` (SSE). Shows: eligible perks with estimated savings and key terms.
  - **Right (Chat)**: `POST /api/perks` (SSE). Compares options for the user’s spend profile and, where allowed, initiates apply flows.
  - **User interaction**: Chat only. MVP read-only; apply flows later.

 - `Advisors & Meetings` (`/advisors`)
  - **Goal**: Connect users to the right advisor at the right time.
  - **Left (Snapshot)**: `POST /api/advisors-snapshot` (SSE). Shows: advisor directory, specialties, and upcoming meetings.
  - **Right (Chat)**: `POST /api/advisors` (SSE). Recommends suitable advisors and schedules/cancels meetings via capabilities when available.
  - **User interaction**: Chat only. MVP read-only; add scheduling next.

- `Profile / Agents` (`/profile`)
  - **Purpose**: Show global “Enable Agents” status and allow toggling on/off.
  - **Data**: `GET /api/agent-status`; `POST /api/agent-status` to update `{ enabled: boolean }`.
  - **UX**: Prominent switch + short explanation of data/API access. When disabled, feature pages are gated.

---

### 4) Backend API Endpoints (responsibilities)

Cross‑cutting for all endpoints: validate session, enforce permissions, guard tool calls, timebox execution, return structured errors, and record basic metrics (latency, tool count).

SSE event contract (all endpoints)
- Wire format: standard SSE with only `data:` lines carrying a JSON envelope per frame; we do not rely on the `event:` field.
- JSON envelope fields we consume (typical):
  - `author`: who emitted the frame (agent/tool)
  - `content.parts[]`: may include `{ text }`, `{ functionCall }`, `{ functionResponse }`
  - `actions.stateDelta`: arbitrary keys for progress/state updates; for snapshots, final frame includes `stateDelta.blocks`
- Client behavior:
  - Chat: append any `content.parts[].text` to the active AI message until stream ends
  - Snapshot: surface progress from `actions.stateDelta.stage` if present; when a frame contains `actions.stateDelta.blocks`, treat it as final and render

#### 4.1 Onboarding & Agent Status

- `POST /api/onboarding/connect-a2a`
  - **Responsibility**: Initialize A2A session with the Cymbal Bank Agent; discover available tools; persist session context; return capabilities summary.
  - **Input**: none (session/user inferred) or `{ userHint?: string }`.
  - **Output**: `{ connected: boolean, tools: string[], permissions: Permission[] }`.

- `GET /api/agent-status`
  - **Responsibility**: Return global agent enablement state.
  - **Output**: `{ enabled: boolean }`.

- `POST /api/agent-status`
  - **Responsibility**: Enable/disable agents globally; persist per user; gate all feature endpoints.
  - **Input**: `{ enabled: boolean }`.
  - **Output**: `{ ok: true, enabled: boolean }`.

#### 4.2 Spending (routes)

- `POST /api/spending-snapshot`
  - **Responsibility**: Orchestrate Snapshot pipeline. Run `SpendingDataAgent` with timeframe → parse JSON → run `SpendingFormatterAgent`.
  - **Transport**: SSE; emit `progress`, optional `tool_start`/`tool_result`, and final `final { blocks }`.
  - **Input**: `{ months?: number }` (default e.g., 6).
  - **Output**: final `final` event with `{ blocks: Block[] }`.

- `POST /api/spending`
  - **Responsibility**: Run `SpendingChatAgent` with the user message and minimal context (e.g., timeframe).
  - **Transport**: SSE; stream `speak { text, partial: true }` frames; optional `tool_start`/`tool_result`; finish with `final { text }`.
  - **Input**: `{ message: string, context?: { months?: number } }`.
  - **Output**: SSE stream.

#### 4.3 Goals (routes)

- `POST /api/goals-snapshot`
  - **Responsibility**: Run `GoalsDataAgent` → `GoalsFormatterAgent`.
  - **Transport**: SSE; emit `progress`, optional `tool_start`/`tool_result`, and final `final { blocks }`.
  - **Input**: `{ }` (optional filters later).
  - **Output**: final `final` event with `{ blocks: Block[] }`.

- `POST /api/goals`
  - **Responsibility**: Run `GoalsChatAgent`; perform goal/schedule updates only when agents are enabled.
  - **Transport**: SSE; stream `speak { text, partial: true }` frames; optional `tool_start`/`tool_result`; finish with `final { text }`.
  - **Input**: `{ message: string }`.
  - **Output**: SSE stream.

#### 4.4 Debts & Investments (Portfolio routes)

- `POST /api/portfolio-snapshot`
  - **Responsibility**: Run `DebtsInvestmentsDataAgent` → `DebtsInvestmentsFormatterAgent`.
  - **Transport**: SSE; emit `progress`, optional `tool_start`/`tool_result`, and final `final { blocks }`.
  - **Output**: final `final` event with `{ blocks: Block[] }`.

- `POST /api/portfolio`
  - **Responsibility**: Run `DebtsInvestmentsChatAgent` for payoff/allocation Q&A.
  - **Transport**: SSE; stream `speak { text, partial: true }` frames; optional `tool_start`/`tool_result`; finish with `final { text }`.
  - **Output**: SSE stream.

#### 4.5 Perks (renamed from Partners & Offers)

- `POST /api/perks-snapshot`
  - **Responsibility**: Run `PerksDataAgent` → `PerksFormatterAgent`; return offers/perks table and savings insight.
  - **Transport**: SSE; emit `progress`, optional `tool_start`/`tool_result`, and final `final { blocks }`.
  - **Output**: final `final` event with `{ blocks: Block[] }`.

- `POST /api/perks`
  - **Responsibility**: Run `PerksChatAgent`; compare/apply eligible perks.
  - **Transport**: SSE; stream `speak { text, partial: true }` frames; optional `tool_start`/`tool_result`; finish with `final { text }`.
  - **Output**: SSE stream.

#### 4.6 Advisors & Meetings (routes)

- `POST /api/advisors-snapshot`
  - **Responsibility**: Run `AdvisorsDataAgent` → `AdvisorsFormatterAgent`; return advisors and meetings blocks.
  - **Transport**: SSE; emit `progress`, optional `tool_start`/`tool_result`, and final `final { blocks }`.
  - **Output**: final `final` event with `{ blocks: Block[] }`.

- `POST /api/advisors`
  - **Responsibility**: Run `AdvisorsChatAgent`; schedule/cancel meetings as permitted.
  - **Transport**: SSE; stream `speak { text, partial: true }` frames; optional `tool_start`/`tool_result`; finish with `final { text }`.
  - **Output**: SSE stream.

---

### 5) ADK Plan (agents, structure, and responsibilities)

#### 5.1 Shared Schemas (Formatter output)

- `ChartSpec(kind, x_field, y_field, x_values, y_values, x_format?, y_format?)`
- `InsightBlock(type="insight", body, title?)`
- `ChartBlock(type="chart", spec, meta?)`
- `TableBlock(type="table", columns, rows, meta?)`
- `Block = InsightBlock | ChartBlock | TableBlock`
- `BlocksOutput(blocks: Block[])`

Notes: Only FormatterAgents use `output_schema=BlocksOutput`. DataAgents and ChatAgents must not use `output_schema` so they can call capabilities on the black‑box A2A agent. ChatAgents should emit streaming responses when possible.

#### 5.2 Spending Agents

- `SpendingDataAgent`
  - **Purpose**: Fetch raw spending data for last N months and summarize into a minimal JSON snapshot string.
  - **Inputs**: `months`.
  - **Tools**: `get_user_transactions_with_history`, `get_user_cashflow`.
  - **Output**: JSON string with fields: `by_category {labels[], values[]}`, `by_month {labels[], values[]}`, `top_merchants [[Merchant, Spend, Count], ...]`, `summary`, `highlight`.
  - **Notes**: No `output_schema`. Robust to sparse data; fall back to zeros and empty arrays.

- `SpendingFormatterAgent`
  - **Purpose**: Convert the snapshot JSON into UI blocks.
  - **Inputs**: Parsed JSON from `SpendingDataAgent`.
  - **Tools**: none.
  - **Output Schema**: `BlocksOutput` with `[insight, chart(by_category), chart(by_month), table(top_merchants)]`.

- `SpendingChatAgent`
  - **Purpose**: Concise, action‑oriented spending Q&A (“How do I cut $200/mo?”).
  - **Inputs**: `message`, optional timeframe context.
  - **Tools**: `get_user_transactions_with_history`, `get_user_cashflow` (read). Future write actions behind permissions (e.g., set reminders via schedules when available).
  - **Output**: plaintext guidance and proposed steps.

#### 5.3 Goals Agents

- `GoalsDataAgent`
  - **Purpose**: Aggregate goals and schedules into a progress snapshot.
  - **Tools**: `get_user_goals`, `get_user_schedules`.
  - **Output**: JSON string with goal list, progress metrics, upcoming schedule items, and an insight summary.

- `GoalsFormatterAgent`
  - **Purpose**: Produce blocks: insight, progress chart (e.g., percent to target), upcoming tasks table.
  - **Tools**: none.
  - **Output Schema**: `BlocksOutput`.

- `GoalsChatAgent`
  - **Purpose**: Plan and manage goals through conversation.
  - **Tools (read)**: `get_user_goals`, `get_user_schedules`.
  - **Tools (write, gated)**: `create_user_goal`, `update_user_goal`, `delete_user_goal`, `create_user_schedule`, `update_user_schedule`, `delete_user_schedule`.
  - **Output**: plaintext confirmation, suggestions, and next steps.

#### 5.4 Debts & Investments Agents (Portfolio)

- `DebtsInvestmentsDataAgent`
  - **Purpose**: Fetch debts, investments, and net worth history to summarize portfolio state.
  - **Tools**: `get_user_debts`, `get_user_investments`, `get_user_networth`.
  - **Output**: JSON string with net worth trend, allocation by asset class, liabilities breakdown, insight.

- `DebtsInvestmentsFormatterAgent`
  - **Purpose**: Blocks: insight, net worth trend chart, allocation chart, liabilities table.
  - **Tools**: none.
  - **Output Schema**: `BlocksOutput`.

- `DebtsInvestmentsChatAgent`
  - **Purpose**: Answer payoff prioritization and allocation questions; propose safe steps.
  - **Tools**: read tools above; write actions only if later provided and permitted.
  - **Output**: plaintext.

#### 5.5 Partners & Offers Agents

- `PartnersDataAgent`
  - **Purpose**: List bank partners and user‑eligible offers; compute estimated savings.
  - **Tools**: `get_bank_partners`, `get_user_eligible_partners`.
  - **Output**: JSON string with offers table fields and savings insight.

- `PartnersFormatterAgent`
  - **Purpose**: Blocks: insight (estimated savings) and offers table.
  - **Tools**: none.
  - **Output Schema**: `BlocksOutput`.

- `PartnersChatAgent`
  - **Purpose**: Compare/apply offers conversationally.
  - **Tools**: read tools above; apply action only if a write tool is available and permitted.
  - **Output**: plaintext.

#### 5.6 Advisors & Meetings Agents

- `AdvisorsDataAgent`
  - **Purpose**: Retrieve advisors and upcoming meetings; summarize availability.
  - **Tools**: `get_all_advisors`, `get_advisors_by_type`, `get_user_meetings`.
  - **Output**: JSON string with advisors list, meetings list, and insight.

- `AdvisorsFormatterAgent`
  - **Purpose**: Blocks: insight, advisors table, upcoming meetings table.
  - **Tools**: none.
  - **Output Schema**: `BlocksOutput`.

- `AdvisorsChatAgent`
  - **Purpose**: Schedule/cancel meetings based on intent.
  - **Tools**: read tools above; write tools `schedule_meeting`, `cancel_meeting` if available and permitted.
  - **Output**: plaintext confirmations.

#### 5.7 Onboarding Agent

- `OnboardingAgent`
  - **Purpose**: Welcome, summarize capabilities, and suggest initial goals; does not alter data.
  - **Tools**: read tools as needed; no writes.
  - **Output**: plaintext suggestions; optionally sets initial snapshot timeframe preference.

#### 5.8 Automation Commitments (for judging)

- **Consumer‑facing automation**: Unused subscription detection (Spending) → suggest cancel or set a budget reminder. If a cancel tool is unavailable, create a schedule reminder via `create_user_schedule` with user permission.
- **Bank‑operations automation**: Advisor meeting scheduling (Advisors) → propose best‑fit advisor and schedule via `schedule_meeting` when enabled; alternative is applying an eligible partner offer if a write tool exists.

---

### 6) Orchestration & Guards

- **Snapshot flow**: API handler validates request and global `enabled` status → run `<Page>DataAgent` (tools allowed) → parse JSON → run `<Page>FormatterAgent` with `output_schema=BlocksOutput` → return `{ blocks }` (non‑streaming).
- **Chat flow**: API handler validates global `enabled` status → run `<Page>ChatAgent` with user message and minimal context → stream tokens until final response.
- **Permissions gate**: All feature endpoints require global agents to be enabled; write tool invocations are additionally contingent on agent enablement.
- **Resilience**: Timeouts and fallbacks; if Formatter validation fails, return a minimal fallback `insight` block explaining the issue.

---

### 7) Implementation Order (hackathon‑friendly)

1) Schemas and shared UI: `Block` models (backend) and `SnapshotRenderer`/`ChatPane` (frontend).
2) Onboarding connect + global enable‑agents endpoints and UI; add `EnableAgentsGate`.
3) Spending: DataAgent, FormatterAgent, endpoints, and page wiring.
4) Goals: DataAgent, FormatterAgent, endpoints, and page wiring.
5) Chat agents for Spending and Goals; enable read tools first; toggle‑gated writes where available.
6) Stub remaining pages/endpoints with placeholder content; upgrade if time allows.
7) Add one consumer automation (subscription reminders) and one bank‑ops automation (meeting scheduling).

---

### 8) Testing & Quality Gates

- **Formatter unit tests**: Validate `BlocksOutput` shape for typical and sparse data.
- **Endpoint smoke tests**: 200 response, timing budget, error envelopes.
- **Tool guard tests**: Verify writes are blocked without permissions; allowed when enabled.
- **UX checks**: Empty states and error banners are shown; no blocking spinners.

---

### 9) Risks & Mitigations

- **Tool gaps**: If write tools are missing, fall back to reminders/suggestions; keep UX consistent.
- **Sparse data**: Ensure charts render empty safely; always include an `insight` explaining missing data.
- **Time constraints**: Lock on Spending/Goals first; keep others read‑only.


---

### 10) Future Implementation (nice‑to‑haves after core logic)

- DatabaseSessionService (Supabase)
  - Replace in‑memory session/artifact/memory services with a Postgres‑backed implementation via Supabase.
  - Tables (suggested):
    - sessions: `id (pk)`, `user_id`, `app_name`, `created_at`, `updated_at`, `state (jsonb)`
    - messages: `id (pk)`, `session_id (fk)`, `role`, `content (jsonb)`, `created_at`
    - artifacts: `id (pk)`, `session_id (fk)`, `name`, `payload (jsonb)`, `created_at`
  - Wiring: inject `DatabaseSessionService` into ADK `Runner`; persist chat transcripts and snapshot artifacts per session.
  - Benefits: durable session history, easy demo reset, cross‑device continuity.

- SSE diagnostics
  - Add optional `event: "progress"` detail payloads for A2A capability phases (e.g., `bank_agent.request_started`, `.response_received`).
  - Add `debug: true` query to endpoints to emit tool_start/tool_end events with redacted args/output previews.

- Chat UX polish
  - Token level streaming cursor; retry last request; copy‑to‑clipboard.
  - System prompts visible in dev mode.

- Caching layer
  - Cache last successful snapshot per page for quick reloads; TTL 5–10 minutes.

- Access control
  - If time allows, add per‑automation toggles beneath the global enable switch.


---

### 11) Quick Reference

- Host agent (A2A) patterns and routing examples:
  - Weather & Airbnb Planner host (routing + remote agent connection): `refs/a2a-samples/samples/python/hosts/weather_and_airbnb_planner/`
    - See `routing_agent.py` for multi-skill routing patterns
    - See `remote_agent_connection.py` for remote agent wiring
  - A2A ADK host runner with streaming: check `refs/ep2-ai-agent-bake-off/a2a_example/a2a_cymbal_bank_agent/agent_executor.py`

- EP2 Sandbox (FE/BE wiring reference): `refs/ep2-ai-agent-bake-off/ep2-sandbox/`
  - Backend: see `backend/` for FastAPI route structure and request models
  - Frontend: see `frontend/` for fetch + streaming handling and API proxying
  - Tests: see `tests/` for end-to-end patterns; `docker-compose.yml` for local wiring

- SSE in ADK and A2A
  - We use standard SSE with only `data:` lines carrying ADK JSON envelopes (`author`, `content.parts`, `actions.stateDelta`).
  - Ensure headers: `Content-Type: text/event-stream`, `Cache-Control: no-cache`, `Connection: keep-alive`.

- Capability-based A2A calls (black box)
  - Ask for capabilities (e.g., “spending history”, “goals list”, “schedule meeting”) rather than specific internal tools
  - Handle partial/unavailable capabilities gracefully and surface fallback insights


---

### 12) Page Q&A Test Prompts (use as acceptance tests for agent behavior)

- Spending
  - How am I tracking against my budget for [category] this month?
  - Where can I cut $[amount]/month without impacting essentials?
  - Based on my cashflow, what is a realistic monthly savings potential?
  - Identify unused subscriptions and propose actions (remind or cancel).
  - Which categories increased most month-over-month, and by how much?
  - Show top merchants by spend for the last [N] months.
  - Surface any relevant cashback/discount opportunities (link out to Perks).

- Goals
  - Create a savings plan to reach $[target] for [goal] by [date]. How much per month?
  - What’s my progress toward [goal]? What tasks are upcoming?
  - Adjust my goal: change target amount/date for [goal].
  - Set a recurring reminder/schedule to transfer $[amount] monthly to my [goal] fund.
  - For a big purchase (house/car/rent $[price]): can I afford it given my income/savings?
  - If I aim for a [trip] costing $[amount] by [date], how much should I save monthly?

- Portfolio (Debts & Investments)
  - What is my current net worth trend over the last [N] months?
  - How is my portfolio allocated by asset class? Any over-concentration?
  - List my current debts with balances, APRs, and minimum payments.
  - In what order should I pay off debts to minimize interest (debt avalanche vs snowball)?
  - Before a large loan, which debts should I reduce first to improve affordability?

- Perks (Offers)
  - What perks or offers am I currently eligible for, and estimated savings?
  - Are there any travel-related offers that could offset my upcoming trip costs?
  - Compare [offer A] vs [offer B]; which saves me more given my spend profile?
  - Apply [offer/perk] to my account (if capability is available).

- Advisors & Meetings
  - Recommend an advisor for [topic], considering availability this week.
  - Schedule a 30-minute meeting with an advisor on [date/time window].
  - List my upcoming meetings and provide reschedule/cancel options.
  - Summarize the last advisor interaction notes (if available) and next steps.

---

### 13) Build Plan (day-of execution order)

1) Host agent scaffolding (replicate working patterns)
   - Copy patterns from `refs/a2a_friend_scheduling/host_agent_adk/` and `refs/a2a-samples/samples/python/hosts/weather_and_airbnb_planner/`.
   - Keep the runner/services minimal and in-memory for speed.

2) Convert weather_and_airbnb host entrypoint to FastAPI
   - Update its `__main__.py` to expose FastAPI endpoints instead of launching Gradio.
   - Start non-streaming (simple POST request, JSON response), verify end-to-end.
   - After baseline works, add SSE streaming (standard `text/event-stream` with ADK JSON envelopes on `data:` lines).

3) Implement first host: Snapshot Host Agent
   - Focus solely on snapshot workflow (DataAgent → FormatterAgent result returned as `{ blocks }`).
   - Treat A2A agent as black-box capabilities; no internal tool names.
   - Return a minimal but correct `BlocksOutput` for Spending first.

4) NextJS app in parallel
   - Initialize app, wire Supabase, and store global "Enable Agents" status.
   - Create two-pane layout; add a polished theme, animated logo, and a modern primary (blue). Working name: `Fi` (financial AI agent).
   - Add `/profile` page to toggle the global enable switch.

5) Wire frontend snapshot flow
   - Implement `/api/spending-snapshot` in NextJS that forwards to Snapshot Host (non-streaming first).
   - Render returned `blocks` with `SnapshotRenderer`; verify charts and tables look good.
   - Repeat pattern for `/api/goals-snapshot` if time allows.

6) Add SSE to snapshot once stable
   - Switch forwarding route to stream SSE and parse ADK JSON envelopes (`content.parts`, `actions.stateDelta`).
   - Show progress (optional) and render final `blocks` when received.

7) Orchestrator Host Agent
   - Create an Orchestrator host that delegates to per-page sub-agents based on route/context:
     - Spending (`/spending`)
     - Goals (`/goals`)
     - Debts & Investments (`/portfolio`)
     - Perks (`/perks`)
     - Advisors & Meetings (`/advisors`)
   - Keep chat non-blocking and capability-based; add SSE later if time.

8) Frontend chat wiring
   - Implement `/api/<feature>` chat endpoints that forward to Orchestrator (start non-streaming, then SSE).
   - Accumulate `content.parts[].text` as frames arrive; close on stream end.

9) Polish and stabilize
   - Verify Page Q&A Test Prompts on Spending and Goals.
   - Ensure charts are visually appealing and responsive.
   - Add minimal error handling and empty states.
