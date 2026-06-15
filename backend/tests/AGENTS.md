# DOX framework

## Purpose

- Owns backend automated tests, e2e tests, manual test helpers, and verification scripts.

## Ownership

- Root files in this folder cover pytest suites and milestone verification.
- `e2e/` owns lifecycle-level tests.
- `manual/` owns manual or exploratory test helpers.

## Local Contracts

- Keep tests aligned with current API contracts, authentication requirements, and database setup.
- Maintain sibling `.md` docs for test and verification source files when test purpose, setup, or expected coverage changes.
- Prefer focused regression tests for bug fixes and broader tests for shared service or schema behavior.

## Work Guidance

- Use pytest naming already configured in `backend/pyproject.toml`.
- Avoid tests that depend on hidden local state unless explicitly marked/manual.

## Verification

- Run `python -m pytest` from `backend/` for the full configured suite.
- Run targeted tests while iterating, then broaden when shared behavior is touched.

## Child DOX Index

- No child AGENTS.md files currently.
