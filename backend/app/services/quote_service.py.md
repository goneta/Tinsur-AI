# quote_service.py

Source: `backend/app/services/quote_service.py`
Documentation: `backend/app/services/quote_service.py.md`
Nearest DOX: `backend/app/AGENTS.md`

## Purpose

- Business service or integration source.
- Keep this sibling document updated when the source file's responsibilities, public behavior, side effects, or verification expectations change.

## Notes

- Handles premium calculation and quote lifecycle (create / accept).
- `validate_policy_ready_underwriting(quote)` requires a current approved `QuoteUnderwritingSnapshot`; it uses the shared `APPROVED_UNDERWRITING_DECISIONS` set and `snapshot_is_expired()` from `underwriting_service` (single source of truth for decision vocabulary + tz-tolerant expiry).
- Do not re-inline a `{"approve","approved"}` literal here — the engine emits `"accept"`, so use the shared constant or issue will wrongly reject accepted quotes.

## Verification

- Follow the verification guidance in the nearest applicable DOX contract.
