# QuoteDetailsModal.tsx

Source: `frontend/components/modals/QuoteDetailsModal.tsx`
Documentation: `frontend/components/modals/QuoteDetailsModal.tsx.md`
Nearest DOX: `frontend/components/AGENTS.md`

## Purpose

- Shows quote details in a modal, fetches detailed quote data, and lets the user select or close the quote.

## Notes

- Uses `react-i18next` for modal copy; do not import `useTranslation` from `next-i18next`.
- Fetches details from `/api/v1/quotes/{quote.id}/details`.

## Verification

- Run `npm run lint --workspace=tinsur-ai-frontend` and `npm run build --workspace=tinsur-ai-frontend` after modal changes.
