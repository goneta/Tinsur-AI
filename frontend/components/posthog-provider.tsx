"use client";

import { ReactNode, Suspense, useEffect } from "react";
import { usePathname, useSearchParams } from "next/navigation";
import posthog, { type CaptureResult } from "posthog-js";
import { PostHogProvider as PHProvider, usePostHog } from "posthog-js/react";

interface PostHogProviderProps {
    children: ReactNode;
    posthogKey?: string;
    posthogHost: string;
}

// Attribution query params worth keeping; every other value is dropped so it
// cannot carry a policy, claim, or client identifier.
const MARKETING_PARAMS = new Set([
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "utm_term",
    "utm_content",
    "gclid",
    "fbclid",
    "ref",
]);

// Replace identifier-like path segments (numeric ids, UUIDs, long tokens) so
// policy, claim, client, and payment identifiers never reach event properties.
function sanitizePath(pathname: string): string {
    return pathname
        .split("/")
        .map((segment) => {
            if (/^\d+$/.test(segment)) return ":id";
            if (
                /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(
                    segment,
                )
            ) {
                return ":id";
            }
            if (segment.length >= 20) return ":token";
            return segment;
        })
        .join("/");
}

function sanitizeUrl(rawUrl: string): string {
    try {
        const url = new URL(rawUrl);
        url.pathname = sanitizePath(url.pathname);
        const kept = new URLSearchParams();
        url.searchParams.forEach((value, key) => {
            if (MARKETING_PARAMS.has(key)) kept.append(key, value);
        });
        url.search = kept.toString();
        url.hash = "";
        return url.toString();
    } catch {
        return rawUrl;
    }
}

// Runs on every event before it is sent, so identifiers are stripped from
// autocapture, pageleave, and exception events too, not only the manual pageview.
function sanitizeEventUrls(event: CaptureResult | null): CaptureResult | null {
    const props = event?.properties;
    if (!props) return event;
    if (typeof props.$current_url === "string") {
        props.$current_url = sanitizeUrl(props.$current_url);
    }
    if (typeof props.$referrer === "string") {
        props.$referrer = sanitizeUrl(props.$referrer);
    }
    if (typeof props.$pathname === "string") {
        props.$pathname = sanitizePath(props.$pathname);
    }
    return event;
}

// PostHog is a browser singleton, initialized once for the whole app.
let posthogInitialized = false;

function PostHogPageView() {
    const pathname = usePathname();
    const searchParams = useSearchParams();
    const client = usePostHog();
    // Depend on the query string, not the params object identity, so a re-render
    // with the same query does not fire a duplicate pageview.
    const search = searchParams.toString();

    useEffect(() => {
        if (!pathname || !client) return;
        // The App Router fires no navigation event, so pageviews are captured
        // here. PostHog fills $current_url, which sanitizeEventUrls then scrubs.
        client.capture("$pageview");
    }, [pathname, search, client]);

    return null;
}

export function PostHogProvider({
    children,
    posthogKey,
    posthogHost,
}: PostHogProviderProps) {
    // Init in render (not an effect) so it runs before the first pageview
    // capture, and in the browser only so a missing key never breaks the build.
    if (typeof window !== "undefined" && !posthogInitialized) {
        posthogInitialized = true;
        if (posthogKey) {
            posthog.init(posthogKey, {
                api_host: posthogHost,
                // Pageviews are captured manually in PostHogPageView.
                capture_pageview: false,
                capture_pageleave: true,
                before_send: sanitizeEventUrls,
                // Insurance data: mask every input value in session replay.
                session_recording: {
                    maskAllInputs: true,
                },
            });
        } else if (process.env.NODE_ENV !== "production") {
            console.error(
                "NEXT_PUBLIC_POSTHOG_KEY variable required by PostHog is missing or un-configured, this causes events to be silently missed. This error stops appearing once NEXT_PUBLIC_POSTHOG_KEY is configured",
            );
        }
    }

    return (
        <PHProvider client={posthog}>
            <Suspense fallback={null}>
                <PostHogPageView />
            </Suspense>
            {children}
        </PHProvider>
    );
}
