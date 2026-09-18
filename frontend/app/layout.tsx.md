# layout.tsx

Source: `frontend/app/layout.tsx`
Documentation: `frontend/app/layout.tsx.md`
Nearest DOX: `frontend/app/AGENTS.md`

## Purpose

- Defines the workspace root HTML/body shell, metadata, Apple/Facebook scripts, and client providers for the frontend app.

## Notes

- Uses the system font stack through global CSS and intentionally avoids `next/font/google` so local builds do not require outbound Google Fonts access.
- Wraps pages in `ClientProviders`.
- Reads `NEXT_PUBLIC_POSTHOG_KEY` and `NEXT_PUBLIC_POSTHOG_HOST` server-side (host defaults to the EU cloud) and passes them to `ClientProviders`, the same pattern as `NEXT_PUBLIC_GOOGLE_CLIENT_ID`.

## Verification

- Run `npm run lint --workspace=tinsur-ai-frontend` and `npm run build --workspace=tinsur-ai-frontend` after layout/provider changes.
