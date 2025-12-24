````markdown
# Project Plan: ADK-Based Multi-Agent Banking Application

## 1. Overview

We are building a **multi-page banking application** using the **Google ADK** framework with **A2A integration** to a deployed **Bank ADK Agent**. Each page will have **two completely independent agents**:

1. **Snapshot Agent** — returns **structured chart/table data** for the left pane.
2. **Chat Agent** — handles conversational, action-oriented interactions for the right pane.

**Key design principle:**  
No agent knows about the other. The **page** coordinates calls to both independently.  
The Snapshot Agent uses a **two-step process** (data fetch → formatter) to comply with ADK’s `output_schema` rules.

---

## 2. Architecture Summary

### 2.1 Per Page Structure
Each page has:
- **Left Pane** — visual data from the Snapshot Agent.
- **Right Pane** — conversation from the Chat Agent.

**Snapshot Flow:**
- **Data Agent**: tool-enabled, gathers raw data from Bank ADK Agent via A2A.
- **Formatter Agent**: no tools, `output_schema` enforced, transforms raw data into `blocks[]` for UI rendering.

**Chat Flow:**
- Independent chat agent with relevant tools.
- Returns **plain text** (for hackathon speed).
- May be extended later with its own formatter for structured plans.

### 2.2 Tool Usage
- **Snapshot Data Agent** → uses **read-only A2A proxy tools** (Bank ADK Agent functions).
- **Chat Agent** → uses both read and potential write tools (later with scope enforcement).
- **Formatter Agent** → **no tools**, only formats.

### 2.3 A2A Integration
- All Bank interactions are via **A2A proxy tools** wrapping the deployed Bank ADK Agent.
- No direct database or API calls from UI or other backend layers.

---

## 3. ADK Constraints & Compliance

ADK constraint:
- `output_schema` **disables tool usage** in the same agent run.
- Solution: **two-agent pattern** for Snapshot (Data Agent + Formatter Agent).

**Why this works:**
- Data Agent: tools **enabled**, no `output_schema`.
- Formatter Agent: tools **disabled**, strict `output_schema` for block validation.

---

## 4. Page 1: Spending

### 4.1 Left Pane — Spending Snapshot Agent

**Agent 1: SpendingDataAgent**
- **Instruction**: Fetch spending data for the last N months via tools and return a minimal JSON snapshot:
  ```json
  {
    "by_category": { "labels": [], "values": [] },
    "by_month": { "labels": [], "values": [] },
    "top_merchants": [["Merchant", "Spend", "Count"], ...],
    "summary": "one sentence",
    "highlight": "one short highlight"
  }
````

* **Tools**:

  * `get_user_transactions_with_history`
  * `get_user_cashflow`
* **Output**: JSON string saved to `session.state["spending_snapshot_raw"]`.

**Agent 2: SpendingFormatterAgent**

* **Instruction**: Convert snapshot JSON to:

  ```json
  { "blocks": [insight_block, chart_block, chart_block, table_block] }
  ```
* **Output Schema**: `BlocksOutput` (Pydantic model).
* **Tools**: none.
* **Output Key**: `spending_blocks`.

**Endpoint**:

* `POST /api/spending/snapshot`:

  1. Run SpendingDataAgent → get raw JSON.
  2. Parse JSON → run SpendingFormatterAgent → get `blocks[]`.
  3. Return `{ blocks: [...] }` to UI.

---

### 4.2 Right Pane — Spending Chat Agent

**Agent: SpendingChatAgent**

* **Instruction**: Be concise and action-oriented. Use tools to answer spending-related questions and propose actions.
* **Tools**:

  * `get_user_transactions_with_history`
  * `get_user_cashflow`
  * (later) write tools with scope enforcement (e.g., `update_user_schedule`).
* **Output**: plaintext for now.
* **Endpoint**:

  * `POST /api/spending/chat`: run agent with `message`, return `{ text: string }`.

---

## 5. Replication Pattern for Other Pages

We will **reuse** this two-agent-per-pane architecture for:

### 5.1 Page 2: Goals

* **Snapshot Tools**: `get_user_goals`, `get_user_schedules`
* **Chat Tools**: above + `create_user_goal`, `update_user_goal`, `delete_user_goal`, `create_user_schedule`, `update_user_schedule`, `delete_user_schedule`

### 5.2 Page 3: Debts & Investments

* **Snapshot Tools**: `get_user_debts`, `get_user_investments`, `get_user_networth`
* **Chat Tools**: above + relevant write actions

### 5.3 Page 4: Partners & Offers

* **Snapshot Tools**: `get_bank_partners`, `get_user_eligible_partners`
* **Chat Tools**: same + offer application logic

### 5.4 Page 5: Advisors & Meetings

* **Snapshot Tools**: `get_all_advisors`, `get_advisors_by_type`, `get_user_meetings`
* **Chat Tools**: same + `schedule_meeting`, `cancel_meeting`

---

## 6. Data Structures

### 6.1 `Block` Schema (for Snapshot Formatter Agents)

```python
class ChartSpec(BaseModel):
    kind: Literal["bar", "line", "area"]
    x_field: str
    y_field: str
    x_values: List[Any]
    y_values: List[float]
    x_format: Optional[str] = None
    y_format: Optional[str] = None

class InsightBlock(BaseModel):
    type: Literal["insight"]
    body: str
    title: Optional[str] = None

class ChartBlock(BaseModel):
    type: Literal["chart"]
    spec: ChartSpec
    meta: Optional[Dict[str, Any]] = None

class TableBlock(BaseModel):
    type: Literal["table"]
    columns: List[str]
    rows: List[List[Any]]
    meta: Optional[Dict[str, Any]] = None

Block = Union[InsightBlock, ChartBlock, TableBlock]

class BlocksOutput(BaseModel):
    blocks: List[Block]
```

---

## 7. API Endpoints Summary

**Per Page:**

* `POST /api/<page>/snapshot`

  * Runs: `<Page>DataAgent` → `<Page>FormatterAgent`
  * Returns: `{ blocks: Block[] }`

* `POST /api/<page>/chat`

  * Runs: `<Page>ChatAgent`
  * Returns: `{ text: string }`

---

## 8. Implementation Steps

1. **Define Block schemas** (shared across pages).

2. **Implement DataAgent** for each page:

   * Tool-enabled, no `output_schema`.
   * Returns raw JSON snapshot string.

3. **Implement FormatterAgent** for each page:

   * No tools, strict `output_schema=BlocksOutput`.
   * Consumes parsed JSON from DataAgent.

4. **Implement ChatAgent** for each page:

   * Tool-enabled, no `output_schema`.
   * Returns plaintext (optionally structured later).

5. **Build endpoints** for `/snapshot` and `/chat` per page.

6. **Frontend**:

   * Left pane: fetch `/snapshot`, render blocks.
   * Right pane: send `/chat`, render text.

---

## 9. Advantages of This Plan

* **ADK-Compliant**: Respects `output_schema` limitations.
* **Separation of Concerns**: Snapshot and chat are independent.
* **Reusability**: Pattern replicated across all pages with minimal changes.
* **Extensibility**: Later, add PlanFormatterAgents for structured action plans.
* **Hackathon-Ready**: Fast to implement, minimal integration risk.

---

## 10. Future Enhancements

* **Chart rendering**: Right pane can output chart/table blocks once MVP is stable.
* **Scope management**: Add per-user scope enforcement in write tools.
* **Caching**: Cache snapshots to reduce tool calls.
* **Plan execution**: Right pane actions can trigger backend workflows via A2A.
* **Simulation Mode**: Allow preview of financial impact before executing actions.

---

```
```
