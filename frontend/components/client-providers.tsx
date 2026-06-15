"use client";

import { ReactNode } from "react";
import { Providers } from "./providers";

interface ClientProvidersProps {
    children: ReactNode;
    googleClientId: string;
}

export function ClientProviders({
    children,
    googleClientId,
}: ClientProvidersProps) {
    return (
        <Providers googleClientId={googleClientId}>
            {children}
        </Providers>
    );
}
