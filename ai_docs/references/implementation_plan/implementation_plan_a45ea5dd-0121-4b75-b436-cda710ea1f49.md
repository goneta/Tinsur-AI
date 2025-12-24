# Backend Agent JSON Integration Plan

## Goal
Ensure the Backend Agents output structured JSON blocks that trigger the Frontend Preview Panel.

## The Gap
The Frontend `LeftPanel` looks for:
```regex
```json\s*({ "type": "quote", ... })\s*```
```

The current Agents likely just return text.

## Proposed Changes

### 1. Update `Quote Agent` (`a2a_quote_agent/__main__.py`)
-   **Prompt Engineering**: Add instruction:
    > "When you generate a quote, ALWAYS append a JSON block at the end of your response following this schema: { type: 'quote', ... }"

### 2. Update `Orchestrator Agent` (`a2a_multi_ai_agents/__main__.py`)
-   Ensure it doesn't strip or summarize the JSON away. It needs to pass the sub-agent's output faithfully.

### 3. Restart Mechanism
-   Since agents are running processes, we need to kill and toggle them.
-   Create `backend/scripts/restart_mesh.ps1`.

## Verification
-   User types "Create a quote for Client X".
-   Agent replies "Here is the quote..." followed by the JSON block.
-   Frontend detects JSON -> Updates Right Panel.
