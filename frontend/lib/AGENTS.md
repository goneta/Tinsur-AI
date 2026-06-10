# DOX framework

## Purpose

- Owns workspace frontend API clients, auth helpers, i18n helpers, currency helpers, and shared frontend types under `frontend/lib`.

## Ownership

- `api/` owns grouped lower-level API modules.
- `types/` owns lib-local shared type definitions.
- Top-level `*-api.ts` files own feature API client calls.

## Local Contracts

- Keep API client method signatures aligned with backend endpoints and shared `frontend/types`.
- Maintain each important library source file's sibling `.md` documentation file alongside code changes.
- Match default versus named exports exactly; several existing build failures came from mismatched import style.
- Centralize HTTP behavior through existing API helpers rather than creating one-off fetch logic.

## Work Guidance

- Prefer typed request/response helpers and shared error handling.
- When backend contracts change, update dependent client methods and consuming components together.

## Verification

- Run `npm run lint` from `frontend/`.
- Run `npm run build` from `frontend/` when API exports or shared types change.

## Child DOX Index

- No child AGENTS.md files currently.
