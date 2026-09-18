# posthog-provider.tsx

Source: `frontend/components/posthog-provider.tsx`
Documentation: `frontend/components/posthog-provider.tsx.md`
Nearest DOX: `frontend/components/AGENTS.md`

## Purpose

- Initializes the PostHog browser SDK and provides it to the React tree.
- Captures `$pageview` manually, because the App Router fires no navigation event.
- Keep this sibling document updated when the source file's responsibilities, public behavior, side effects, or verification expectations change.

## Notes

- Takes `posthogKey` and `posthogHost` as props (supplied by `client-providers.tsx` from the root layout); it does not read `process.env` itself.
- Init runs during render, in the browser only, and once (`posthogInitialized`), so it happens before the first pageview capture and a missing key never breaks the build. In development a missing key logs an error; production stays a no-op.
- Autocapture pageviews are off (`capture_pageview: false`); `PostHogPageView` sends `$pageview` on each path change.
- Session replay masks every input value (`maskAllInputs: true`).
- A `before_send` hook (`sanitizeEventUrls`) scrubs `$current_url`, `$referrer`, and `$pathname` on every event: identifier-like path segments become `:id`/`:token` and only marketing query params survive, so policy, claim, client, and payment identifiers stay out of event properties.
- Prefer stable contracts, exported APIs, route behavior, data shape, permissions, side effects, and important dependencies over change history.

## Verification

- Follow the verification guidance in the nearest applicable DOX contract.
