# DOX framework

## Purpose

- Owns workspace public static assets, logos, images, and avatar files.

## Ownership

- `images/` owns bundled product images.
- `avatars/` owns bundled avatar assets.
- Root files own SVGs and favicon-like public assets.

## Local Contracts

- Keep assets optimized enough for web delivery and reference them with stable public paths.
- Do not replace brand assets without checking logo and branding docs where relevant.

## Work Guidance

- Prefer existing logo variants before adding new brand files.
- Update consuming code when asset names or locations change.

## Verification

- Run `npm run build` from `frontend/` when asset paths used by code change.

## Child DOX Index

- No child AGENTS.md files currently.
