import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Providers } from "@/components/providers";

const inter = Inter({
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Tinsur.AI",
  description: "Modern insurance management platform for Côte d'Ivoire",
};

import Script from 'next/script';

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const fbAppId = process.env.NEXT_PUBLIC_FACEBOOK_APP_ID;

  return (
    <html lang="en" suppressHydrationWarning translate="no" className="notranslate">
      <body className={`${inter.className} antialiased`}>
        <Providers googleClientId={process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID || "mock-client-id"}>
          {children}
        </Providers>

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
