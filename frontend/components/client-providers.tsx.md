# client-providers.tsx

Source: `frontend/components/client-providers.tsx`
Documentation: `frontend/components/client-providers.tsx.md`
Nearest DOX: `frontend/components/AGENTS.md`

## Purpose

- React component source.
- Keep this sibling document updated when the source file's responsibilities, public behavior, side effects, or verification expectations change.

## Notes

- Wraps the app in `PostHogProvider` (see `posthog-provider.tsx`), then `Providers`.
- `PostHogProvider` is the outermost wrapper, so PostHog starts before the `Providers` mount gate and captures the first pageview.
- Add concise operational details here when editing the source file.
- Prefer stable contracts, exported APIs, route behavior, data shape, permissions, side effects, and important dependencies over change history.

## Verification

- Follow the verification guidance in the nearest applicable DOX contract.
