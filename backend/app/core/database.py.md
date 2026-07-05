# database.py

Source: `backend/app/core/database.py`
Documentation: `backend/app/core/database.py.md`
Nearest DOX: `backend/app/AGENTS.md`

## Purpose

- Backend infrastructure, configuration, or security source.
- Keep this sibling document updated when the source file's responsibilities, public behavior, side effects, or verification expectations change.

## Notes

- Builds the SQLAlchemy `engine`/`SessionLocal`, plus MongoDB and Redis clients, from `settings`.
- The engine is created with a tolerant `json_serializer` (`json.dumps(..., default=str)`) so JSON/JSONB columns can persist UUID, Decimal, datetime and date values instead of raising `TypeError: Object of type UUID is not JSON serializable`.
- SQLite URLs get WAL + `synchronous=NORMAL` pragmas via a connect listener.
- Prefer stable contracts, exported APIs, route behavior, data shape, permissions, side effects, and important dependencies over change history.

## Verification

- Follow the verification guidance in the nearest applicable DOX contract.
