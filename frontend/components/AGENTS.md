# DOX framework

## Purpose

- Owns workspace shared React components, feature UI, layout UI, modals, forms, and UI primitives.

## Ownership

- `ui/` owns generic primitives.
- Feature folders own domain-specific component behavior.
- `layout/` owns shell, navigation, headers, and shared page framing.

## Local Contracts

- Keep low-level primitives generic and domain components close to their feature folder.
- Maintain each important component source file's sibling `.md` documentation file alongside code changes.
- Maintain import paths consistent with `@/components/...` and existing file locations.

## Work Guidance

- Reuse existing Radix/shadcn-style components and lucide icons.
- Keep component props typed and avoid embedding API calls in generic UI primitives.
- Preserve polished responsive behavior for dashboard and portal workflows.

## Verification

- Run `npm run lint` from `frontend/`.
- Run `npm run build` from `frontend/` for shared component or layout changes.

## Child DOX Index

- No child AGENTS.md files currently.
