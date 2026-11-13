"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

// "paths" lists every address that belongs to the section.
const LINKS = [
    { href: "/quran", label: "Quran", paths: ["/quran", "/surah"] },
    { href: "/learn", label: "Learn", paths: ["/learn"] },
    { href: "/sources", label: "Sources", paths: ["/sources"] },
];

/** The main navigation links. The current section is marked for everyone. */
export default function NavLinks() {
    const pathname = usePathname();

    return (
        <nav
            aria-label="Main"
            className="order-last flex w-full gap-5 sm:order-none sm:w-auto"
        >
            {LINKS.map(({ href, label, paths }) => {
                const active = paths.some(
                    (path) => pathname === path || pathname.startsWith(`${path}/`)
                );
                return (
                    <Link
                        key={href}
                        href={href}
                        aria-current={active ? "page" : undefined}
                        className={
                            active
                                ? "font-semibold text-accent underline underline-offset-4"
                                : "underline-offset-4 hover:underline"
                        }
                    >
                        {label}
                    </Link>
                );
            })}
        </nav>
    );
}