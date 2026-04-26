import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import Script from "next/script";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
  display: "swap",
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "justaskit",
  description: "upload csv → ask question → get answer",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
      suppressHydrationWarning
    >
      <body className="min-h-full flex flex-col" suppressHydrationWarning>
        <Script
          id="strip-bis"
          strategy="beforeInteractive"
          dangerouslySetInnerHTML={{
            __html: `
              document.querySelectorAll('[bis_skin_checked]').forEach(function(el){el.removeAttribute('bis_skin_checked')});
              new MutationObserver(function(m){m.forEach(function(r){if(r.attributeName==='bis_skin_checked')r.target.removeAttribute('bis_skin_checked')})}).observe(document.documentElement,{attributes:true,subtree:true,attributeFilter:['bis_skin_checked']});
            `,
          }}
        />
        {children}
      </body>
    </html>
  );
}
