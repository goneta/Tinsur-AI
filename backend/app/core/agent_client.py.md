# agent_client.py

Source: `backend/app/core/agent_client.py`
Documentation: `backend/app/core/agent_client.py.md`
Nearest DOX: `backend/app/AGENTS.md`

## Purpose

- Backend infrastructure, configuration, or security source.
- Keep this sibling document updated when the source file's responsibilities, public behavior, side effects, or verification expectations change.

## Notes

- `AgentClient.send_message()` posts to a discovered agent URL (`agent_discovery.get_agent_url`) and returns the parsed JSON.
- When an agent is unreachable it returns `{"error": ...}` — it never fabricates a fake success payload (e.g. a "claim filed" message). Callers must treat `{"error": ...}` as failure and run their own fallback.
- HTTP/connection failures are logged and surfaced as `{"error": ...}`; they do not raise.

## Verification

- Follow the verification guidance in the nearest applicable DOX contract.
