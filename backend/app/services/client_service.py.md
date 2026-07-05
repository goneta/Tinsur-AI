# client_service.py

Source: `backend/app/services/client_service.py`
Documentation: `backend/app/services/client_service.py.md`
Nearest DOX: `backend/app/AGENTS.md`

## Purpose

- Business service or integration source.
- Keep this sibling document updated when the source file's responsibilities, public behavior, side effects, or verification expectations change.

## Notes

- `create_client()` / `register_client()` create the Client (and, for self-registration, its backing User) and always link it to the company via the `client_company` M2M using `_link_company()` — regardless of client type. Quote/policy/underwriting lookups join through `client_company`, so this link is required for the client to be visible.
- The API endpoint (`clients.create_client`) is responsible for committing; the service flushes and links but the request handler must `db.commit()` or the client silently disappears.
- `Client.company_id` is a read-only hybrid over the M2M; never assign it directly — append to `client.companies`.

## Verification

- Follow the verification guidance in the nearest applicable DOX contract.
