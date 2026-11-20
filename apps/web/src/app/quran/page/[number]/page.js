import Link from "next/link";
import { notFound } from "next/navigation";

import MushafPageReader from "@/components/MushafPageReader";
import { apiGet } from "@/lib/api";

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

    return (
        <div className="mx-auto max-w-6xl px-4 py-8">
            <p className="text-sm">
                <Link href="/quran" className="underline">
                    The Qur&apos;an
                </Link>{" "}
                / Page {page.number}
            </p>
            <div className="mt-4">
                <MushafPageReader page={page} />
            </div>
        </div>
    );
}