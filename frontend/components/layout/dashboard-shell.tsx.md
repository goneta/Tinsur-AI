# dashboard-shell.tsx

Source: `frontend/components/layout/dashboard-shell.tsx`
Documentation: `frontend/components/layout/dashboard-shell.tsx.md`
Nearest DOX: `frontend/components/AGENTS.md`

## Purpose

- Provides the authenticated dashboard frame for workspace App Router dashboard pages.
- Renders the desktop sidebar, top header, scrollable dashboard content area, and optional global AI workspace panel.
- Renders the mobile sidebar as an overlay controlled by the top header menu action.

## Notes

- Desktop layout uses fixed flex regions so the sidebar remains visible and does not depend on resizable panel hydration.
- The sidebar can collapse to a compact 72px rail; `/dashboard/ai-manager` starts collapsed.
- The global AI workspace opens as a right-side panel on large desktop screens and as a full-screen overlay on mobile.

## Verification

- Run `npm run lint` from `frontend/`.
- Run `npm run build` from `frontend/` for meaningful shell or navigation changes.
