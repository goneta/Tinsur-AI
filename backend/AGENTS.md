# DOX framework

## Purpose

- Owns the Python FastAPI backend, SQLAlchemy data model, Alembic migrations, A2A/AI agents, backend tests, scripts, backend docs, and backend runtime assets.

## Ownership

- `app/AGENTS.md` owns the FastAPI application package.
- `agents/AGENTS.md` owns standalone A2A and AI agent implementations.
- `alembic/AGENTS.md` owns database migrations.
- `tests/AGENTS.md` owns backend pytest, e2e, and manual verification tests.
- Parent-owned backend paths include startup scripts, top-level verification scripts, seed/check helpers, backend reports/logs, `requirements.txt`, `pyproject.toml`, `alembic.ini`, `static/`, `data/`, `google/`, `scripts/`, and vendored `libs/`.

## Local Contracts

- Keep API, model, schema, service, and migration changes consistent; do not change one layer without checking dependent layers.
- UUID primary/foreign keys must use the cross-dialect `app.core.guid.GUID` type, never `sqlalchemy.dialects.postgresql.UUID` directly. Raw postgres `UUID` fails to compile on SQLite (used for local dev/tests); `GUID` renders native `UUID` on Postgres and `CHAR(36)` elsewhere.
- JSON/JSONB columns may hold UUID/Decimal/datetime values; the engine's tolerant `json_serializer` (see `app/core/database.py`) handles them. Do not assume JSON columns only contain JSON-native types.
- Underwriting decision vocabulary and snapshot-expiry logic live in `app/services/underwriting_service.py` (`APPROVED_UNDERWRITING_DECISIONS`, `snapshot_is_expired`); reuse them rather than re-inlining `{"approve",...}` literals or naive datetime comparisons.
- Important backend source files use sibling Markdown docs named by appending `.md` to the source filename; update the sibling doc when source responsibilities, public behavior, side effects, dependencies, or verification expectations change.
- Treat `backend/libs/` as vendored dependency code and avoid editing it unless explicitly required.
- Treat `backend/data/` and `backend/static/documents/` as runtime/generated stores; avoid broad manual edits unless the task is specifically about those artifacts.
- Preserve existing verification scripts and reports unless they are stale and the task includes documentation cleanup.

## Work Guidance

- FastAPI runs from `backend/app/main.py`.
- Use SQLAlchemy models in `app/models`, Pydantic schemas in `app/schemas`, business logic in `app/services`, repositories in `app/repositories`, and routes in `app/api/v1/endpoints`.
- When adding tables or changing persisted fields, update Alembic migrations and related tests or seed scripts.
- Keep security, auth, permissions, payments, AI actions, and document generation changes especially conservative.

## Verification

- Backend tests: run `python -m pytest` from `backend/`.
- Migrations: run `python -m alembic upgrade head` from `backend/` when schema changes are involved.

## Child DOX Index

- `app/AGENTS.md` - FastAPI application package.
- `agents/AGENTS.md` - A2A/AI agent packages and tools.
- `alembic/AGENTS.md` - Alembic migration environment and versions.
- `tests/AGENTS.md` - Backend tests and verification scripts.
