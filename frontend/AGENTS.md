# DOX framework

## Purpose

- Owns the `tinsur-ai-frontend` npm workspace: Next.js app, shared UI, API clients, localization, assets, and frontend-specific docs/config.

## Ownership

- `app/AGENTS.md` owns workspace App Router routes.
- `components/AGENTS.md` owns workspace shared components.
- `lib/AGENTS.md` owns workspace API clients, auth, i18n, currency, and helpers.
- `public/AGENTS.md` owns workspace public assets.
- Parent-owned frontend paths include `config/`, `context/`, `contexts/`, `hooks/`, `messages/`, `services/`, `types/`, frontend docs, Next/Tailwind/ESLint/PostCSS config, build logs, and package files.

## Local Contracts

- Follow `frontend/FRONTEND_RULES.md` for import correctness, export style, component existence, JSX balance, and build recovery.
- Important frontend source files use sibling Markdown docs named by appending `.md` to the source filename; update the sibling doc when source responsibilities, public behavior, side effects, dependencies, or verification expectations change.
- Keep workspace code compatible with root workspace scripts in `package.json`.
- Do not edit generated build output or logs unless the task is explicitly about cleanup or diagnostics.

## Work Guidance

- Next.js App Router, TypeScript, Tailwind CSS, Radix/shadcn-style primitives, TanStack Query, React Hook Form, and Zod are the local frontend stack.
- Prefer existing components, API clients, hooks, and type files before adding new abstractions.
- Keep translations in `messages/` and public locale files consistent when changing user-visible copy.

## Verification

- Run `npm run lint` from `frontend/` for lintable changes.
- Run `npm run build` from `frontend/` or the repository root for route, config, or shared component changes.

## Child DOX Index

- `app/AGENTS.md` - Workspace App Router routes.
- `components/AGENTS.md` - Workspace shared UI and feature components.
- `lib/AGENTS.md` - Workspace frontend clients and utilities.
- `public/AGENTS.md` - Workspace static assets.
