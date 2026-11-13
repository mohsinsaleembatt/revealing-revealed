import Link from "next/link";

import HeroBook from "@/components/HeroBook";

export const metadata = {
    title: "Revealing Revealed",
    description:
        "Learn Arabic and the tools for understanding the Qur'an, through the verses themselves.",
};

const WAYS = [
    {
        step: "1 · Read",
        title: "The Qur'an",
        text: "Read the verified text, surah by surah, in a proper Qur'anic font.",
        href: "/quran",
        cta: "Open the Qur'an",
    },
    {
        step: "2 · Understand",
        title: "Lessons",
        text: "Learn Arabic through the verses themselves. The first lessons are in preparation and are labelled as drafts until a reviewer has checked them.",
        href: "/learn",
        cta: "See the lessons",
    },
    {
        step: "3 · Remember",
        title: "Short quizzes",
        text: "Questions that bring back what you just read, with the reason for every answer.",
        href: "/learn",
        cta: "Try a quiz",
    },
];

const TRUST = [
    {
        title: "Verified text",
        text: "The Qur'an comes from the Tanzil Project and is shown unmodified.",
    },
    {
        title: "Cited lessons",
        text: "Every claim in a lesson names its source.",
    },
    {
        title: "Honest status",
        text: "Each lesson shows whether a qualified reviewer has checked it.",
    },
];

export default function Home() {
    return (
        <>
            <section className="mx-auto grid max-w-6xl items-center gap-12 px-4 py-16 md:grid-cols-[1.1fr_0.9fr]">
                <div>
                    <p className="text-sm font-semibold uppercase tracking-widest text-accent">
                        Arabic through the Qur&apos;an
                    </p>
                    <h1 className="mt-4 font-serif text-4xl font-semibold leading-tight sm:text-5xl">
                        Understand the Qur&apos;an in its own language.
                    </h1>
                    <p className="mt-5 max-w-xl text-lg text-mute sm:text-xl">
                        Learn the Arabic and the tools scholars use, through the verses
                        themselves. Every lesson shows its sources.
                    </p>
                    <p className="mt-8 flex flex-wrap gap-4">
                        <Link
                            href="/learn"
                            className="rounded-lg bg-accent px-6 py-3 font-semibold text-accent-ink"
                        >
                            Start learning
                        </Link>
                        <Link
                            href="/quran"
                            className="rounded-lg border-2 border-accent px-6 py-3 font-semibold text-accent"
                        >
                            Open the Qur&apos;an
                        </Link>
                    </p>
                    <p className="mt-5 text-sm text-mute">
                        Free · No ads · Sources cited
                    </p>
                </div>

                <HeroBook />
            </section>

            <section className="mx-auto max-w-6xl px-4 pb-16">
                <h2 className="font-serif text-3xl font-semibold">
                    Three ways to learn, one verse at a time
                </h2>
                <ul className="mt-6 grid gap-6 md:grid-cols-3">
                    {WAYS.map((way) => (
                        <li
                            key={way.step}
                            className="flex flex-col rounded-2xl border border-line bg-raised p-6"
                        >
                            <p className="font-semibold text-accent">{way.step}</p>
                            <h3 className="mt-1 text-xl font-semibold">{way.title}</h3>
                            <p className="mt-2 flex-1 text-mute">{way.text}</p>
                            <Link href={way.href} className="mt-4 font-semibold text-accent underline underline-offset-4">
                                {way.cta}
                            </Link>
                        </li>
                    ))}
                </ul>
            </section>

            <section className="bg-band">
                <div className="mx-auto max-w-6xl px-4 py-14">
                    <h2 className="font-serif text-2xl font-semibold">Built on trust</h2>
                    <ul className="mt-6 grid gap-8 md:grid-cols-3">
                        {TRUST.map((item) => (
                            <li key={item.title}>
                                <p className="font-semibold">{item.title}</p>
                                <p className="mt-1 text-mute">{item.text}</p>
                            </li>
                        ))}
                    </ul>
                </div>
            </section>
        </>
    );
}