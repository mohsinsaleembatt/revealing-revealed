import "./globals.css";
import Link from "next/link";

export const metadata = {
  title: "Revealing Revealed",
  description: "Learn the tools for understanding the Qur'an, starting with Arabic.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className="flex min-h-screen flex-col">
        <header className="border-b border-black/10 dark:border-white/20">
          <div className="mx-auto flex max-w-4xl items-center justify-between px-4 py-4">
            <Link href="/" className="text-lg font-semibold">
              Revealing Revealed
            </Link>
            <nav className="flex gap-4 text-sm">
              <Link href="/learn" className="underline">
                Learn
              </Link>
            </nav>
          </div>
        </header>

        <main className="mx-auto w-full max-w-4xl flex-1 px-4 py-8">
          {children}
        </main>

        <footer className="border-t border-black/10 text-sm dark:border-white/20">
          <div className="mx-auto max-w-4xl px-4 py-6 opacity-80">
            Qur&apos;anic text from the{" "}
            <a
              href="https://tanzil.net"
              target="_blank"
              rel="noopener noreferrer"
              className="underline"
            >
              Tanzil Project (tanzil.net)
            </a>
            , licensed under Creative Commons Attribution 3.0 and shown
            unmodified. <Link href="/sources" className="underline">Sources and notices</Link>
          </div>
        </footer>
      </body>
    </html>
  );
}