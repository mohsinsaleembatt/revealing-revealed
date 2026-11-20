import Link from "next/link";

import { apiGet } from "@/lib/api";

export const metadata = { title: "The Qur'an | Revealing Revealed" };

export default async function QuranPage() {
    const juzList = await apiGet("/quran/juz");

    return (
        <div className="container-reading">
            <h1 className="font-serif text-3xl font-semibold">The Qur&apos;an</h1>
            <p className="mt-2 text-mute">
                The Qur&apos;an in its 30 traditional parts. Choose one to see its
                surahs.
            </p>

            <div
                role="list"
                aria-label="The 30 juz of the Qur'an, sized by number of verses"
                className="mt-6 flex overflow-hidden rounded-lg border border-line"
            >
                {juzList.map((juz) => (
                    <Link
                        key={juz.number}
                        href={`/quran/juz/${juz.number}`}
                        role="listitem"
                        title={`Juz ${juz.number}: ${juz.start_reference} to ${juz.end_reference} (${juz.ayah_count} verses)`}
                        style={{ flexGrow: juz.ayah_count }}
                        className="flex items-center justify-center border-r border-line bg-raised py-4 text-xs font-medium last:border-r-0 hover:bg-band"
                    >
                        {juz.number}
                    </Link>
                ))}
            </div>

            <p className="mt-8 flex flex-wrap gap-6 text-sm">
                <Link href="/quran/surahs" className="underline">
                    Browse by surah
                </Link>
                <Link href="/surah/1" className="underline">
                    Start from Al-Faatiha
                </Link>
                <Link href="/quran/page/1" className="underline">
                    Read by Mushaf page
                </Link>
            </p>
        </div>
    );
}