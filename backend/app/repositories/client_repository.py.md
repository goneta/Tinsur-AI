# client_repository.py

Source: `backend/app/repositories/client_repository.py`
Documentation: `backend/app/repositories/client_repository.py.md`
Nearest DOX: `backend/app/AGENTS.md`

## Purpose

- Data access repository source.
- Keep this sibling document updated when the source file's responsibilities, public behavior, side effects, or verification expectations change.

## Notes

- Company-scoped queries (`get_by_id`, `get_all`, `count`) join `Client.companies` and filter on `Company.id == company_id`. Do **not** filter on `client_company.c.company_id` after `join(Client.companies)` — that reintroduces the association table as a second FROM element and produces a cartesian product (duplicate rows / inflated counts on Postgres).
- `create()` excludes `password`, `company_id`, and `automobile_details` from the model kwargs; company linkage is done by the service layer via the M2M.

## Verification

- Follow the verification guidance in the nearest applicable DOX contract.
