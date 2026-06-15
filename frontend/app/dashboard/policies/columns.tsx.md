# columns.tsx

Source: `frontend/app/dashboard/policies/columns.tsx`
Documentation: `frontend/app/dashboard/policies/columns.tsx.md`
Nearest DOX: `frontend/app/AGENTS.md`

## Purpose

- Defines the policy table columns and row action menu for the workspace dashboard policies route.

## Notes

- The translation callback accepts an optional fallback string, matching `frontend/contexts/language-context.tsx`.
- Keep action callbacks deferred with the existing `setTimeout` pattern unless the surrounding table action flow changes.

## Verification

- Run `npm run lint --workspace=tinsur-ai-frontend` and `npm run build --workspace=tinsur-ai-frontend` after table column changes.
