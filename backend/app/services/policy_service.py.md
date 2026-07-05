# policy_service.py

Source: `backend/app/services/policy_service.py`
Documentation: `backend/app/services/policy_service.py.md`
Nearest DOX: `backend/app/AGENTS.md`

## Purpose

- Business service or integration source.
- Keep this sibling document updated when the source file's responsibilities, public behavior, side effects, or verification expectations change.

## Notes

- `create_from_quote()` issues a policy only when the quote is accepted/policy_created, not expired, and has an approved, unexpired `QuoteUnderwritingSnapshot` (uses shared `APPROVED_UNDERWRITING_DECISIONS` + `snapshot_is_expired()` from `underwriting_service`).
- After creation it triggers reinsurance cession, archival, and document generation. Document generation calls `ClientRepository.get_by_id(client_id, company_id)` — the second (company) argument is required; it is best-effort and non-blocking.
- Premium attribution for commissions flows from payment processing, not here.

## Verification

- Follow the verification guidance in the nearest applicable DOX contract.
