# DOX framework

## Purpose

- Owns root-level frontend API clients, auth helpers, navigation helpers, shared utilities, and lib-local types.

## Ownership

- `api/` owns grouped API modules.
- `types/` owns lib-local shared TypeScript types.
- Top-level `*-api.ts` files own feature-specific API client wrappers.

## Local Contracts

- Keep root-level clients aligned with root-level routes/components and backend endpoint contracts.
- Maintain each important library source file's sibling `.md` documentation file alongside code changes.
- Match import/export style exactly and verify target files before adding imports.
- Avoid duplicating client behavior that already exists in another root-level lib module.

## Work Guidance

- Prefer existing `api.ts` and feature clients for HTTP behavior.
- Update shared types alongside API contract changes.

## Verification

- Run `npm run lint` or `npm run build` from the repository root when clients, types, or shared utilities change.

## Child DOX Index

- No child AGENTS.md files currently.
