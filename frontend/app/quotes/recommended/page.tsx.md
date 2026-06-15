# page.tsx

Source: `frontend/app/quotes/recommended/page.tsx`
Documentation: `frontend/app/quotes/recommended/page.tsx.md`
Nearest DOX: `frontend/app/AGENTS.md`

## Purpose

- Renders recommended quote options after auto-generation for a client.

## Notes

- Uses `react-i18next` for `useTranslation`; do not import the hook from `next-i18next`.
- Redirects to quote creation when no `client_id` query parameter is present.

## Verification

- Run `npm run lint --workspace=tinsur-ai-frontend` and `npm run build --workspace=tinsur-ai-frontend` after route changes.
