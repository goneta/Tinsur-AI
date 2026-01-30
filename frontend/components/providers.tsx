"use client";

import { ReactNode } from "react";
import { GoogleOAuthProvider } from '@react-oauth/google';
import { ThemeProvider } from "./theme-provider";
import { LanguageProvider } from "../contexts/language-context";
import { QueryProvider } from "./query-provider";
import { AuthProvider } from "../lib/auth";
import { BrandingProvider } from "./branding-provider";
import { Toaster } from "./ui/toaster";

interface ProvidersProps {
    children: ReactNode;
    googleClientId: string;
}

export function Providers({ children, googleClientId }: ProvidersProps) {
    return (
        <GoogleOAuthProvider clientId={googleClientId}>
            <ThemeProvider defaultTheme="light" storageKey="insurance-saas-theme">
                <LanguageProvider>
                    <QueryProvider>
                        <AuthProvider>
                            <BrandingProvider>
                                {children}
                                <Toaster />
                            </BrandingProvider>
                        </AuthProvider>
                    </QueryProvider>
                </LanguageProvider>
            </ThemeProvider>
        </GoogleOAuthProvider>
    );
}
