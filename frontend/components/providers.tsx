"use client";

import { useState, useEffect, ReactNode } from "react";
import { GoogleOAuthProvider } from '@react-oauth/google';
import { ThemeProvider } from "./theme-provider";
import { LanguageProvider } from "../contexts/language-context";
import { QueryProvider } from "./query-provider";
import { AuthProvider } from "../lib/auth";
import { BrandingProvider } from "./branding-provider";
import { Toaster as SonnerToaster } from "sonner";
import { Toaster } from "./ui/toaster";
import Script from "next/script";

interface ProvidersProps {
    children: ReactNode;
    googleClientId: string;
}

export function Providers({ children, googleClientId }: ProvidersProps) {
    const [mounted, setMounted] = useState(false);

    useEffect(() => {
        setMounted(true);
    }, []);

    if (!mounted) {
        return <div className="min-h-screen bg-background" />;
    }

    return (
        <GoogleOAuthProvider clientId={googleClientId}>
            <ThemeProvider defaultTheme="light" storageKey="insurance-saas-theme">
                <LanguageProvider>
                    <QueryProvider>
                        <AuthProvider>
                            <BrandingProvider>
                                {children}
                                <Toaster />
                                <SonnerToaster position="top-right" richColors />
                            </BrandingProvider>
                        </AuthProvider>
                    </QueryProvider>
                </LanguageProvider>
            </ThemeProvider>
        </GoogleOAuthProvider>
    );
}
