# underwriting_service.py

Source: `backend/app/services/underwriting_service.py`
Documentation: `backend/app/services/underwriting_service.py.md`
Nearest DOX: `backend/app/AGENTS.md`

## Purpose

- Business service or integration source.
- Keep this sibling document updated when the source file's responsibilities, public behavior, side effects, or verification expectations change.

## Notes

- `deterministic_quote_underwriting()` runs the rule engine and, when persisting, writes an `UnderwritingDecision` and a `QuoteUnderwritingSnapshot` (with `valid_until = utcnow() + 30 days`, timezone-aware).
- Exposes shared helpers used by the quote/policy issue paths:
  - `APPROVED_UNDERWRITING_DECISIONS = {"accept","accepted","approve","approved"}` — the decision vocabulary that clears a quote for policy issue (the engine emits `"accept"`).
  - `snapshot_is_expired(valid_until)` — tz-tolerant expiry check that treats naive stored datetimes as UTC.
- `quote_service` and `policy_service` import both helpers; keep the vocabulary/expiry logic here as the single source of truth.
- Snapshot JSON columns hold UUID/Decimal values; persistence relies on the engine's tolerant `json_serializer` (see `core/database.py`).

## Verification

- Follow the verification guidance in the nearest applicable DOX contract.
