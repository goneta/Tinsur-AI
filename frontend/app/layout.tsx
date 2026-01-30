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

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning translate="no" className="notranslate">
      <body className={`${inter.className} antialiased`}>
        <Providers googleClientId={process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID || "mock-client-id"}>
          {children}
        </Providers>
      </body>
    </html>
  );
}
