# CurrencyInput.tsx

Source: `frontend/components/forms/CurrencyInput.tsx`
Documentation: `frontend/components/forms/CurrencyInput.tsx.md`
Nearest DOX: `frontend/components/AGENTS.md`

## Purpose

- Provides a locale-aware FCFA currency input with parsing and formatting on blur.

## Notes

- Uses `react-i18next` for the active language when choosing decimal formatting.
- Calls `onChange` with numeric values parsed from the displayed text.

## Verification

- Run `npm run lint --workspace=tinsur-ai-frontend` and `npm run build --workspace=tinsur-ai-frontend` after form input changes.
