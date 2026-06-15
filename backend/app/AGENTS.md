# DOX framework

## Purpose

- Owns the FastAPI application package and core backend domain implementation.

## Ownership

- `api/v1/endpoints/` owns HTTP route handlers and request/response orchestration.
- `models/` owns SQLAlchemy persistence models.
- `schemas/` owns Pydantic request/response schemas.
- `services/` owns business logic and integrations.
- `repositories/` owns database access helpers.
- `core/` owns settings, security, database wiring, middleware, and shared infrastructure.
- `tasks/`, `scripts/`, `middleware/`, `templates/`, and `utils/` are owned here unless a child DOX is added later.

## Local Contracts

- Keep router registration, schemas, services, repositories, and models in sync for each feature.
- Maintain each important source file's sibling `.md` documentation file alongside code changes.
- Do not bypass permission, auth, rate-limit, or AI action-control services when adding endpoints or agent-triggered operations.
- Validate external inputs at the schema or endpoint boundary before they reach services.

## Work Guidance

- Prefer small endpoint functions that delegate business behavior to services.
- Use repository helpers for repeated database queries rather than scattering query logic.
- Keep document templates and generated document behavior compatible with existing static document output.

## Verification

- Run targeted backend tests from `backend/`, for example `python -m pytest tests/test_auth.py`.
- Run the wider backend suite with `python -m pytest` for shared service, schema, auth, payment, AI, or persistence changes.

## Child DOX Index

- No child AGENTS.md files currently.
