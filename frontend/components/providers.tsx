"use client";

import { ReactNode } from "react";
import { GoogleOAuthProvider } from '@react-oauth/google';
import { ThemeProvider } from "@/components/theme-provider";
import { LanguageProvider } from "@/contexts/language-context";
import { QueryProvider } from "@/components/query-provider";
import { AuthProvider } from "@/lib/auth";
import { BrandingProvider } from "@/components/branding-provider";
import { Toaster } from "@/components/ui/toaster";

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
