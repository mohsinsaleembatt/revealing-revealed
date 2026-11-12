import Link from "next/link";
import { notFound } from "next/navigation";

import { apiGet } from "@/lib/api";
import { quranFont } from "@/lib/fonts";

/** Turn the address part into a surah number from 1 to 114, or null. */
function parseSurahNumber(value) {
    const number = Number(value);
    return Number.isInteger(number) && number >= 1 && number <= 114 ? number : null;
}

/** Tell Next.js which surah pages exist, so it can prepare them in advance. */
export function generateStaticParams() {
    return Array.from({ length: 114 }, (_, index) => ({
        number: String(index + 1),
    }));
}

export async function generateMetadata({ params }) {
    const { number } = await params;
    const surahNumber = parseSurahNumber(number);
    if (surahNumber === null) return {};
    const surah = await apiGet(`/quran/surahs/${surahNumber}`);
    return { title: surah ? `${surah.name_transliteration} | Revealing Revealed` : undefined };
}

export default async function SurahPage({ params }) {
    const { number } = await params;
    const surahNumber = parseSurahNumber(number);
    if (surahNumber === null) notFound();

    const surah = await apiGet(`/quran/surahs/${surahNumber}`);
    if (!surah) notFound();

    return (
        <article>
            <header className="text-center">
                <p className="opacity-70">
                    Surah {surah.number} · {surah.revelation_place}
                </p>
                <h1 dir="rtl" lang="ar" className={`${quranFont.className} mt-2 text-4xl leading-[1.8]`}>
                    {surah.name_arabic}
                </h1>
                <p className="mt-2 text-xl">
                    {surah.name_transliteration} — {surah.name_english}
                </p>
                <p className="opacity-70">{surah.ayah_count} verses</p>
            </header>

            <div
                dir="rtl"
                lang="ar"
                className={`${quranFont.className} mt-10 space-y-6 text-3xl leading-[2.4] sm:text-4xl`}
            >
                {surah.ayahs.map((ayah) => (
                    <p key={ayah.number} id={`ayah-${ayah.number}`}>
                        {ayah.text_uthmani}{" "}
                        <span className="inline-block min-w-8 rounded-full border border-current px-2 text-center text-lg opacity-70">
                            {ayah.number.toLocaleString("ar-EG")}
                        </span>
                    </p>
                ))}
            </div>

            <nav className="mt-12 flex justify-between">
                {surahNumber > 1 ? (
                    <Link href={`/surah/${surahNumber - 1}`} className="underline">
                        ← Previous surah
                    </Link>
                ) : (
                    <span />
                )}
                {surahNumber < 114 ? (
                    <Link href={`/surah/${surahNumber + 1}`} className="underline">
                        Next surah →
                    </Link>
                ) : (
                    <span />
                )}
            </nav>
        </article>
    );
}