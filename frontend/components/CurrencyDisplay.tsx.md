# CurrencyDisplay.tsx

Source: `frontend/components/CurrencyDisplay.tsx`
Documentation: `frontend/components/CurrencyDisplay.tsx.md`
Nearest DOX: `frontend/components/AGENTS.md`

## Purpose

- Displays FCFA currency amounts using the shared `formatAmount` helper.

## Notes

- Uses `react-i18next` for the active language when no `locale` prop is provided.
- Supports small, medium, and large text sizes plus optional currency-label hiding.

## Verification

- Run `npm run lint --workspace=tinsur-ai-frontend` and `npm run build --workspace=tinsur-ai-frontend` after component changes.
