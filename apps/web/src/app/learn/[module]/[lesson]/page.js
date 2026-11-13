import Link from "next/link";
import { notFound } from "next/navigation";

import ReviewBadge from "@/components/ReviewBadge";
import { apiGet } from "@/lib/api";
import { quranFont } from "@/lib/fonts";

import Quiz from "@/components/Quiz";

export default async function LessonPage({ params }) {
    const { module, lesson: lessonSlug } = await params;
    const lesson = await apiGet(
        `/learn/modules/${encodeURIComponent(module)}/lessons/${encodeURIComponent(lessonSlug)}`
    );
    if (!lesson) notFound();

    const questions =
        (await apiGet(
            `/learn/modules/${encodeURIComponent(module)}/lessons/${encodeURIComponent(lessonSlug)}/quiz`,
            { fresh: true }
        )) ?? [];

    return (
        <article className="container-reading">
            <p className="text-sm opacity-70">
                <Link href="/learn" className="underline">
                    Learn
                </Link>{" "}
                / {lesson.module_title}
            </p>

            <h1 className="mt-2 text-3xl font-semibold">{lesson.title}</h1>
            <p className="mt-2 opacity-70">{lesson.goal}</p>
            <div className="mt-3">
                <ReviewBadge status={lesson.review_status} />
            </div>

            {lesson.review_status === "draft" && (
                <p
                    role="note"
                    className="mt-4 rounded-lg border border-current p-3 text-sm"
                >
                    This lesson is a draft. It has not yet been checked by a qualified
                    reviewer, so please do not rely on it.
                </p>
            )}

            <div className="mt-8 space-y-8">
                {lesson.blocks.map((block) => (
                    <section key={block.position}>
                        {block.kind === "text" && (
                            <>
                                <p className="whitespace-pre-line leading-relaxed">{block.body}</p>
                                {block.source_name && (
                                    <p className="mt-1 text-xs opacity-70">
                                        Source: {block.source_name}
                                        {block.source_location ? `, ${block.source_location}` : ""}
                                    </p>
                                )}
                            </>
                        )}

                        {block.kind === "ayah" && (
                            <figure className="rounded-lg border border-black/10 p-4 dark:border-white/20">
                                <p
                                    dir="rtl"
                                    lang="ar"
                                    className={`${quranFont.className} text-3xl leading-[2.4]`}
                                >
                                    {block.ayah_text}
                                </p>
                                <figcaption className="mt-2 text-sm opacity-70">
                                    Qur&apos;an {block.ayah_reference}
                                    {" · "}
                                    <Link
                                        href={`/surah/${block.ayah_reference.split(":")[0]}#ayah-${block.ayah_reference.split(":")[1]}`}
                                        className="underline"
                                    >
                                        open in the reader
                                    </Link>
                                    {block.note ? ` · ${block.note}` : ""}
                                </figcaption>
                            </figure>
                        )}
                    </section>
                ))}
            </div>

            {questions.length > 0 && (
                <section className="mt-12">
                    <h2 className="text-2xl font-semibold">Check your understanding</h2>
                    <p className="mt-1 text-sm opacity-70">
                        These questions are generated automatically from the verified
                        Qur&apos;an data and are still waiting for review.
                    </p>
                    <div className="mt-4">
                        <Quiz questions={questions} />
                    </div>
                </section>
            )}
        </article>
    );
}