"use client";

import dynamic from 'next/dynamic';
import { ReactNode } from 'react';

// Dynamically import the main Providers component with SSR disabled
const Providers = dynamic(
    () => import('./providers').then((mod) => mod.Providers),
    { ssr: false }
);

interface ClientProvidersProps {
    children: ReactNode;
    googleClientId: string;
}

export function ClientProviders({ children, googleClientId }: ClientProvidersProps) {
    return (
        <Providers googleClientId={googleClientId}>
            {children}
        </Providers>
    );
}
