# DOX framework

## Purpose

- Owns Alembic migration configuration and database schema version files.

## Ownership

- `env.py` and `script.py.mako` define migration execution behavior.
- `versions/` contains ordered migration revisions.

## Local Contracts

- Every persisted model change that affects the database schema needs an Alembic revision or an explicit reason why it does not.
- Maintain sibling `.md` docs for migration source files and note schema intent, data impact, and verification expectations.
- Keep migrations deterministic and compatible with existing production data where possible.

## Work Guidance

- Prefer additive or carefully staged migrations for production data safety.
- Include downgrade behavior when feasible and consistent with existing revisions.

## Verification

- Run `python -m alembic upgrade head` from `backend/` after migration changes.
- Run affected backend tests when schemas or data behavior change.

## Child DOX Index

- No child AGENTS.md files currently.
