# tools.py

Source: `backend/agents/a2a_document_agent/tools.py`
Documentation: `backend/agents/a2a_document_agent/tools.py.md`
Nearest DOX: `backend/agents/AGENTS.md`

## Purpose

- AI/A2A agent implementation source.
- Keep this sibling document updated when the source file's responsibilities, public behavior, side effects, or verification expectations change.

## Notes

- Exposes `generate_payment_schedule_pdf(db, policy_id, user_id)` and `generate_policy_agreement_pdf(db, policy_id, user_id)`; both build a reportlab PDF, persist it under `static/documents/<client_id>/`, and create a `Document` row.
- `Document` rows are written with `company_id=policy.company_id` (FK to companies — required, must not be a client id), plus `policy_id` and `client_id` populated.
- Consumed by the `POST /policies/{id}/generate-schedule` and `.../generate-agreement` endpoints.

## Verification

- Follow the verification guidance in the nearest applicable DOX contract.
