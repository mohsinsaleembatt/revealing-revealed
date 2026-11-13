import "./globals.css";
import { Source_Sans_3, Source_Serif_4 } from "next/font/google";

import SiteFooter from "@/components/SiteFooter";
import SiteHeader from "@/components/SiteHeader";

// Interface font and heading font. Next.js serves them from our own site.
const sans = Source_Sans_3({
  subsets: ["latin"],
  variable: "--font-sans-ui",
  display: "swap",
});
const serif = Source_Serif_4({
  subsets: ["latin"],
  variable: "--font-serif-ui",
  display: "swap",
});

export const metadata = {
  title: "Revealing Revealed",
  description: "Learn the tools for understanding the Qur'an, starting with Arabic.",
};

export const instant = false;

// Runs before the page is drawn, so a saved dark theme never flashes light first.
const THEME_SCRIPT = `try{if(localStorage.getItem("theme")==="dark")document.documentElement.dataset.theme="dark"}catch(e){}`;

export default function RootLayout({ children }) {
  return (
    // suppressHydrationWarning: the script above may change <html> before React starts.
    <html
      lang="en"
      className={`${sans.variable} ${serif.variable}`}
      suppressHydrationWarning
    >
      <head>
        <script dangerouslySetInnerHTML={{ __html: THEME_SCRIPT }} />
      </head>
      <body className="flex min-h-screen flex-col">
        <a
          href="#main"
          className="sr-only focus:not-sr-only focus:absolute focus:left-2 focus:top-2 focus:z-50 focus:rounded-lg focus:bg-accent focus:px-4 focus:py-2 focus:text-accent-ink"
        >
          Skip to content
        </a>
        <SiteHeader />
        <main id="main" className="flex-1">
          {children}
        </main>
        <SiteFooter />
      </body>
    </html>
  );
}