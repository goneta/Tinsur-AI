# chat.py

Source: `backend/app/api/v1/endpoints/chat.py`
Documentation: `backend/app/api/v1/endpoints/chat.py.md`
Nearest DOX: `backend/app/AGENTS.md`

## Purpose

- HTTP endpoint or route handler source.
- Keep this sibling document updated when the source file's responsibilities, public behavior, side effects, or verification expectations change.

## Notes

- `POST /` is the orchestrator chat entrypoint. It degrades through three strategies so a single failing layer never returns a raw 500:
  1. In-process `MultiAgentExecutor` (any import/runtime failure — including dependency conflicts — falls through, and an `"Orchestrator Error:"`/`"Error calling Gemini"` text response is treated as a failure).
  2. HTTP `AgentClient` to a running agent service.
  3. Direct `LLMRouter.generate()` (same provider hierarchy as the websocket path).
- If every strategy fails it raises `503` with the real provider error (e.g. an invalid/leaked API key), never a fabricated success message.
- `WS /ws` streams tokens via `AiService.get_llm_router(...)`; auth is by `token` query param.
- Prompt-safety (`AiHardeningService`) and AI-credit checks (`get_effective_ai_config`) run before any provider call; CREDIT plans consume usage via `log_and_consume_usage`.
- Requires a valid AI provider key in the environment/company config; the chat is only as reliable as that credential.

## Verification

- Follow the verification guidance in the nearest applicable DOX contract.
