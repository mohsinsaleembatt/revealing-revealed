import Link from "next/link";
import { notFound } from "next/navigation";

import { apiGet } from "@/lib/api";

function parseJuzNumber(value) {
    const number = Number(value);
    return Number.isInteger(number) && number >= 1 && number <= 30 ? number : null;
}

export function generateStaticParams() {
    return Array.from({ length: 30 }, (_, index) => ({ number: String(index + 1) }));
}

export default async function JuzPage({ params }) {
    const { number } = await params;
    const juzNumber = parseJuzNumber(number);
    if (juzNumber === null) notFound();

    const juz = await apiGet(`/quran/juz/${juzNumber}`);
    if (!juz) notFound();

    const maxVerses = Math.max(...juz.surahs.map((surah) => surah.verses_in_juz));

    return (
        <div className="container-reading">
            <p className="text-sm">
                <Link href="/quran" className="underline">
                    The Qur&apos;an
                </Link>{" "}
                / Juz {juz.number}
            </p>
            <h1 className="mt-2 font-serif text-3xl font-semibold">Juz {juz.number}</h1>
            <p className="mt-1 text-mute">
                {juz.start_reference} to {juz.end_reference} · {juz.ayah_count} verses
            </p>

            <ul className="mt-6 grid gap-3 sm:grid-cols-2">
                {juz.surahs.map((surah) => (
                    <li key={surah.number}>
                        <Link
                            href={`/surah/${surah.number}#ayah-${surah.first_ayah_number}`}
                            className="block rounded-lg border border-line bg-raised p-4 hover:bg-band"
                        >
                            <span className="flex items-center justify-between gap-3">
                                <span className="font-medium">
                                    {surah.number}. {surah.name_transliteration}
                                </span>
                                <span dir="rtl" lang="ar" className="text-lg">
                                    {surah.name_arabic}
                                </span>
                            </span>
                            <span className="mt-1 block text-sm text-mute">
                                {surah.is_complete
                                    ? `Full surah · ${surah.total_verses} verses`
                                    : `Verses ${surah.first_ayah_number}–${surah.last_ayah_number} of ${surah.total_verses}`}
                            </span>
                            <span
                                className="mt-2 block h-1.5 rounded-full bg-accent"
                                style={{
                                    width: `${Math.max(8, (surah.verses_in_juz / maxVerses) * 100)}%`,
                                }}
                            />
                        </Link>
                    </li>
                ))}
            </ul>

            <nav className="mt-10 flex justify-between text-sm">
                {juzNumber > 1 ? (
                    <Link href={`/quran/juz/${juzNumber - 1}`} className="underline">
                        ← Juz {juzNumber - 1}
                    </Link>
                ) : (
                    <span />
                )}
                {juzNumber < 30 ? (
                    <Link href={`/quran/juz/${juzNumber + 1}`} className="underline">
                        Juz {juzNumber + 1} →
                    </Link>
                ) : (
                    <span />
                )}
            </nav>
        </div>
    );
}