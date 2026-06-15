# page.tsx

Source: `app/page.tsx`
Documentation: `app/page.tsx.md`
Nearest DOX: `app/AGENTS.md`

## Purpose

- Next.js route page source.
- Re-exports the workspace landing page implementation from `frontend/app/page.tsx` so the root-level route mirror stays aligned with the active frontend workspace.

## Notes

- Keep this file minimal unless the root-level app becomes the actively served frontend surface.
- Update `frontend/app/page.tsx.md` when homepage behavior changes.

## Verification

- Verify the active workspace page with `npm run lint` and `npm run build`.
