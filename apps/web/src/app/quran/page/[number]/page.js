import { Fragment } from "react";
import Link from "next/link";
import { notFound } from "next/navigation";

import { apiGet } from "@/lib/api";
import { quranFont } from "@/lib/fonts";

function parsePageNumber(value) {
    const number = Number(value);
    return Number.isInteger(number) && number >= 1 && number <= 604 ? number : null;
}

export default async function MushafPageView({ params }) {
    const { number } = await params;
    const pageNumber = parsePageNumber(number);
    if (pageNumber === null) notFound();

    const page = await apiGet(`/quran/pages/${pageNumber}`);
    if (!page) notFound();

    const surahByNumber = Object.fromEntries(
        page.surahs.map((surah) => [surah.number, surah])
    );
    const surahNames = page.surahs.map((s) => s.name_transliteration).join(" · ");

    return (
        <div className="container-reading">
            <p className="text-sm">
                <Link href="/quran" className="underline">
                    The Qur&apos;an
                </Link>{" "}
                / Page {page.number}
            </p>

            <article
                className="relative mx-auto mt-4 aspect-[1/1.414] w-full max-w-xl rounded-sm border border-line bg-page px-8 py-10 shadow-lg sm:px-12"
                aria-label={`Mushaf page ${page.number}`}
            >
                <div
                    aria-hidden="true"
                    className="pointer-events-none absolute inset-3 border border-gold"
                />

                <header className="relative flex justify-between text-sm text-mute">
                    <span>{surahNames}</span>
                    <span>{page.juz_number ? `Juz ${page.juz_number}` : ""}</span>
                </header>

                <div
                    dir="rtl"
                    lang="ar"
                    className={`${quranFont.className} relative mt-8 text-2xl leading-[2.5] sm:text-3xl`}
                    style={{ textAlign: "justify" }}
                >
                    {page.verses.map((verse) => (
                        <Fragment key={`${verse.surah_number}:${verse.number}`}>
                            {verse.number === 1 && (
                                <div className="my-4 rounded-sm border border-gold py-1 text-center">
                                    {surahByNumber[verse.surah_number].name_arabic}
                                </div>
                            )}
                            <span id={`ayah-${verse.surah_number}-${verse.number}`}>
                                {verse.text_uthmani}
                            </span>{" "}
                            <span className="mx-1 inline-block min-w-7 rounded-full border border-current px-1 text-center font-sans text-sm opacity-80">
                                {verse.number.toLocaleString("ar-EG")}
                            </span>{" "}
                        </Fragment>
                    ))}
                </div>

                <footer className="relative mt-8 text-center text-sm text-mute">
                    {page.number}
                </footer>
            </article>

            <nav
                aria-label="Page navigation"
                className="mx-auto mt-6 flex max-w-xl justify-between text-sm"
            >
                {pageNumber < 604 ? (
                    <Link href={`/quran/page/${pageNumber + 1}`} className="underline">
                        ← Next page
                    </Link>
                ) : (
                    <span />
                )}
                {pageNumber > 1 ? (
                    <Link href={`/quran/page/${pageNumber - 1}`} className="underline">
                        Previous page →
                    </Link>
                ) : (
                    <span />
                )}
            </nav>
        </div>
    );
}