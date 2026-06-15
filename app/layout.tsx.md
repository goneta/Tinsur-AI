# layout.tsx

Source: `app/layout.tsx`
Documentation: `app/layout.tsx.md`
Nearest DOX: `app/AGENTS.md`

## Purpose

- Defines the root-level mirror app layout, providers, metadata, and global shell.

## Notes

- Uses the system font stack and intentionally avoids `next/font/google` so local builds do not require outbound Google Fonts access.
- Keep this mirror aligned with the active frontend workspace while both app trees exist.

## Verification

- Verify the active workspace with `npm run lint --workspace=tinsur-ai-frontend` and `npm run build --workspace=tinsur-ai-frontend`.
