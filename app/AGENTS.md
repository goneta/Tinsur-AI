# DOX framework

## Purpose

- Owns the root-level Next.js App Router route tree, layouts, pages, global styles, and route-local assets.

## Ownership

- Covers dashboard, portal, auth, help, verification, and root pages under `app/`.
- Shared route UI that is reused across routes should live in `components/`; route-specific pieces may stay near the route.

## Local Contracts

- Keep route files aligned with the shared frontend contracts in root `components/`, `lib/`, `messages/`, `public/`, and `types/`.
- Maintain each important route source file's sibling `.md` documentation file alongside code changes.
- Do not duplicate business logic in pages when an existing API client or shared service can own it.

## Work Guidance

- Use App Router conventions: `page.tsx`, `layout.tsx`, route groups, and dynamic segments as already used in the tree.
- Match import style to the actual export style and verify imported files exist before adding imports.
- Keep JSX balanced and test impacted routes when layout or navigation changes.

## Verification

- Run `npm run lint` or `npm run build` from the repository root when route changes are meaningful.

## Child DOX Index

- No child AGENTS.md files currently.
