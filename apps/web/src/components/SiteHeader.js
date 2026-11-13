import Link from "next/link";

import NavLinks from "@/components/NavLinks";
import ThemeToggle from "@/components/ThemeToggle";

export default function SiteHeader() {
    return (
        <header className="border-b border-line bg-paper">
            <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-x-6 gap-y-2 px-4 py-3">
                <Link href="/" className="font-serif text-xl font-semibold">
                    Revealing Revealed
                </Link>
                <NavLinks />
                <ThemeToggle />
            </div>
        </header>
    );
}