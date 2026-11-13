import Link from "next/link";

export default function SiteFooter() {
    return (
        <footer className="border-t border-line bg-band text-sm">
            <div className="mx-auto max-w-6xl px-4 py-8">
                <div className="grid gap-6 sm:grid-cols-3">
                    <div>
                        <p className="font-serif text-lg font-semibold">Revealing Revealed</p>
                        <p className="mt-1 text-mute">
                            Tools for understanding the Qur&apos;an, beginning with Arabic.
                        </p>
                    </div>
                    <nav aria-label="Explore">
                        <p className="font-semibold">Explore</p>
                        <ul className="mt-1 space-y-1">
                            <li>
                                <Link href="/quran" className="underline">The Qur&apos;an</Link>
                            </li>
                            <li>
                                <Link href="/learn" className="underline">Learn</Link>
                            </li>
                        </ul>
                    </nav>
                    <nav aria-label="About">
                        <p className="font-semibold">About</p>
                        <ul className="mt-1 space-y-1">
                            <li>
                                <Link href="/sources" className="underline">Sources and notices</Link>
                            </li>
                        </ul>
                    </nav>
                </div>

                <p className="mt-8 border-t border-line pt-4 text-mute">
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
                    unmodified. Lessons marked Draft are pending scholarly review.
                </p>
            </div>
        </footer>
    );
}