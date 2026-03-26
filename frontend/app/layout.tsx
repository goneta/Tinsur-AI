import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Tinsur.AI",
  description: "Modern insurance management platform for Côte d'Ivoire",
};

import Script from 'next/script';
import { ClientProviders } from '@/components/client-providers';

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const fbAppId = process.env.NEXT_PUBLIC_FACEBOOK_APP_ID;

  return (
    <html lang="en" suppressHydrationWarning translate="no" className="notranslate">
      <head>
        {/* Apple Sign In SDK - Load early (client handles readiness/polling) */}
        <Script
          id="apple-sdk"
          src="https://appleid.cdn-apple.com/appleauth/static/jsapi/appleid/auth/v1/appleid.auth.js"
          strategy="beforeInteractive"
        />
      </head>
      <body className={`${inter.className} antialiased`}>
        <ClientProviders googleClientId={process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID || "mock-client-id"}>
          {children}
        </ClientProviders>

        {/* Facebook SDK */}
        {fbAppId && fbAppId !== "mock-fb-id" && (
          <Script
            id="fb-sdk"
            strategy="afterInteractive"
            dangerouslySetInnerHTML={{
              __html: `
                window.fbAsyncInit = function() {
                  FB.init({
                    appId      : '${fbAppId}',
                    cookie     : true,
                    xfbml      : true,
                    version    : 'v18.0'
                  });
                };
                (function(d, s, id){
                   var js, fjs = d.getElementsByTagName(s)[0];
                   if (d.getElementById(id)) {return;}
                   js = d.createElement(s); js.id = id;
                   js.src = "https://connect.facebook.net/en_US/sdk.js";
                   fjs.parentNode.insertBefore(js, fjs);
                 }(document, 'script', 'facebook-jssdk'));
              `,
            }}
          />
        )}
      </body>
    </html>
  );
}
