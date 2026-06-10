# DOX framework

## Purpose

- Owns workspace Next.js App Router routes, layouts, global CSS, and route-local UI.

## Ownership

- Covers auth, dashboard, portal, quote, verification, and root pages under `frontend/app/`.
- Shared components used by multiple routes belong in `frontend/components/`.

## Local Contracts

- Keep route behavior aligned with `frontend/lib` API clients and `frontend/types` contracts.
- Maintain each important route source file's sibling `.md` documentation file alongside code changes.
- Use route-local code only when it is not broadly reusable.

## Work Guidance

- Follow App Router file conventions already present in this folder.
- Add `"use client"` only when component behavior requires client-side hooks, events, or browser APIs.
- Verify page imports exist and match default/named exports before finishing changes.

## Verification

- Run `npm run lint` from `frontend/` for route changes.
- Run `npm run build` from `frontend/` for meaningful routing, layout, or global CSS changes.

## Child DOX Index

- No child AGENTS.md files currently.
