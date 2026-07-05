# llm_router.py

Source: `backend/app/services/llm_router.py`
Documentation: `backend/app/services/llm_router.py.md`
Nearest DOX: `backend/app/AGENTS.md`

## Purpose

- Business service or integration source.
- Keep this sibling document updated when the source file's responsibilities, public behavior, side effects, or verification expectations change.

## Notes

- Unified async interface over Gemini / OpenAI / Anthropic with `generate()` and `stream()`; provider auto-detected from key shape unless set explicitly.
- Fallback is key-aware: `_priority_list()` only includes a fallback provider when its SDK is installed **and** a dedicated env key exists (`GOOGLE_API_KEY` / `OPENAI_API_KEY` / `ANTHROPIC_API_KEY`). A single provider-specific key is never reused across providers, so a Gemini key no longer produces misleading "anthropic not installed" errors.
- `_provider_key(provider)` resolves the correct key per provider; each `_call_*` uses it.
- `build_router_from_config(...)` picks the provider from company preference → system `AI_CONFIG` → env hints → key shape.

## Verification

- Follow the verification guidance in the nearest applicable DOX contract.
