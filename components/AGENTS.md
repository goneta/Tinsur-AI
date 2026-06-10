# DOX framework

## Purpose

- Owns root-level shared React components, feature components, layout components, and UI primitives.

## Ownership

- `ui/` owns shadcn-style primitives and reusable low-level controls.
- Feature folders such as `admin/`, `ai-agent/`, `analytics/`, `claims/`, `clients/`, `portal/`, `quotes/`, `payments/`, `policies/`, and `support/` own domain UI.
- `layout/` owns dashboard shell, navigation, header, notification, and AI panel layout components.

## Local Contracts

- Components must be reusable from root-level App Router routes and match existing TypeScript/Tailwind patterns.
- Maintain each important component source file's sibling `.md` documentation file alongside code changes.
- Verify imports against actual file locations before adding or moving shared components.
- Keep UI primitives generic; put domain behavior in feature folders.

## Work Guidance

- Use lucide icons where existing UI uses icons.
- Match existing component style and avoid unnecessary wrapper cards or nested card layouts.
- Keep client components explicit with `"use client"` when hooks or browser APIs are used.

## Verification

- Run `npm run lint` or `npm run build` from the repository root for meaningful component changes.

## Child DOX Index

- No child AGENTS.md files currently.
