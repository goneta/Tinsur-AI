# page.tsx

Source: `frontend/app/page.tsx`
Documentation: `frontend/app/page.tsx.md`
Nearest DOX: `frontend/app/AGENTS.md`

## Purpose

- Next.js route page source.
- Implements the public TinsurAI landing page with fixed navigation, hero, AI automation tasks, insurance types, agent feature cards, pricing plans, image gallery, and contact form.
- Keeps `/register`, `/login`, and anchored navigation visible from the homepage.

## Notes

- Uses remote realistic imagery in standard `img` elements to avoid Next image domain configuration.
- Uses `LanguageSwitcher` from `frontend/components/language-switcher.tsx`.
- The page is intentionally public and no longer redirects anonymous users to `/login`.

## Verification

- Run `npm run lint` and `npm run build` from `frontend/` or through the root workspace after meaningful homepage changes.
