"use client";

import { ReactNode } from "react";
import { Providers } from "./providers";
import { PostHogProvider } from "./posthog-provider";

interface ClientProvidersProps {
    children: ReactNode;
    googleClientId: string;
    posthogKey?: string;
    posthogHost: string;
}

export function ClientProviders({
    children,
    googleClientId,
    posthogKey,
    posthogHost,
}: ClientProvidersProps) {
    return (
        <PostHogProvider posthogKey={posthogKey} posthogHost={posthogHost}>
            <Providers googleClientId={googleClientId}>
                {children}
            </Providers>
        </PostHogProvider>
    );
}
