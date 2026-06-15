# DOX framework

## Purpose

- Owns root-level public assets and locale JSON served by the root-level Next.js app.

## Ownership

- `locales/` owns public translation JSON grouped by locale.
- Root files own SVG and static image assets.

## Local Contracts

- Keep locale keys synchronized across languages when changing translated UI.
- Preserve stable asset paths used by routes and components.

## Work Guidance

- Prefer adding locale values in all supported locales touched by the feature.
- Update consuming code when asset names or locations change.

## Verification

- Run `npm run build` from the repository root when public asset paths or locale loading behavior changes.

## Child DOX Index

- No child AGENTS.md files currently.
