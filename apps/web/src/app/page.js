import Link from "next/link";

import { apiGet } from "@/lib/api";
import { quranFont } from "@/lib/fonts";

export default async function Home() {
  const surahs = await apiGet("/quran/surahs");

  return (
    <div>
      <h1 className="text-3xl font-semibold">The Qur&apos;an</h1>
      <p className="mt-2 opacity-70">Choose a surah to read.</p>

      <ul className="mt-6 grid gap-3 sm:grid-cols-2">
        {surahs.map((surah) => (
          <li key={surah.number}>
            <Link
              href={`/surah/${surah.number}`}
              className="flex items-center justify-between gap-4 rounded-lg border border-black/10 p-4 hover:bg-black/5 dark:border-white/20 dark:hover:bg-white/10"
            >
              <span>
                <span className="block font-medium">
                  {surah.number}. {surah.name_transliteration}
                </span>
                <span className="block text-sm opacity-70">
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