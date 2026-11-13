import Link from "next/link";

import { apiGet } from "@/lib/api";
import { quranFont } from "@/lib/fonts";

export const metadata = { title: "The Qur'an | Revealing Revealed" };

export default async function QuranPage() {
    const surahs = await apiGet("/quran/surahs");

    return (
        <div className="container-reading">
            <h1 className="font-serif text-3xl font-semibold">The Qur&apos;an</h1>
            <p className="mt-2 text-mute">Choose a surah to read.</p>

            <ul className="mt-6 grid gap-3 sm:grid-cols-2">
                {surahs.map((surah) => (
                    <li key={surah.number}>
                        <Link
                            href={`/surah/${surah.number}`}
                            className="flex items-center justify-between gap-4 rounded-lg border border-line bg-raised p-4 hover:bg-band"
                        >
                            <span>
                                <span className="block font-medium">
                                    {surah.number}. {surah.name_transliteration}
                                </span>
                                <span className="block text-sm text-mute">
                                    {surah.name_english} · {surah.ayah_count} verses
                                </span>
                            </span>
                            <span dir="rtl" lang="ar" className={`${quranFont.className} text-2xl`}>
                                {surah.name_arabic}
                            </span>
                        </Link>
                    </li>
                ))}
            </ul>
        </div>
    );
}