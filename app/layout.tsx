import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { AuthProvider } from "@/lib/auth";
import { ThemeProvider } from "@/components/theme-provider";
import { BrandingProvider } from "@/components/branding-provider";

import { Toaster } from "@/components/ui/toaster";

const inter = Inter({
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Tinsur.AI",
  description: "Modern insurance management platform for Côte d'Ivoire",
};

import { QueryProvider } from "@/components/query-provider";
import { LanguageProvider } from "@/contexts/language-context";
import { GoogleOAuthProvider } from "@react-oauth/google";

// import { cookies } from 'next/headers';
// import { I18nProvider } from "@/components/i18n-provider";
// import enMessages from "@/messages/en.json";
// import frMessages from "@/messages/fr.json";
// import esMessages from "@/messages/es.json";

// const MESSAGES = {
//   en: enMessages,
//   fr: frMessages,
//   es: esMessages,
// };

export default async function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  // const cookieStore = await cookies();
  // const locale = cookieStore.get('NEXT_LOCALE')?.value || 'en';
  // const messages = MESSAGES[locale as keyof typeof MESSAGES] || enMessages;

  return (
    <html lang="en" suppressHydrationWarning translate="no" className="notranslate">
      <body className={`${inter.className} antialiased`}>
        <GoogleOAuthProvider clientId={process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID || ""}>
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
      </body>
    </html>
  );
}
