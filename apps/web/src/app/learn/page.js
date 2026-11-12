import Link from "next/link";

import ReviewBadge from "@/components/ReviewBadge";
import { apiGet } from "@/lib/api";

export const metadata = { title: "Learn | Revealing Revealed" };

export default async function LearnPage() {
    const modules = await apiGet("/learn/modules");

    return (
        <div>
            <h1 className="text-3xl font-semibold">Learn</h1>
            <p className="mt-2 opacity-70">
                Lessons are labelled with their review status.
            </p>

            {modules.map((module) => (
                <section key={module.slug} className="mt-8">
                    <h2 className="text-xl font-semibold">
                        Module {module.number}: {module.title}
                    </h2>
                    <p className="mt-1 opacity-70">{module.summary}</p>

                    <ul className="mt-4 space-y-2">
                        {module.lessons.map((lesson) => (
                            <li key={lesson.slug}>
                                <Link
                                    href={`/learn/${module.slug}/${lesson.slug}`}
                                    className="flex items-center justify-between gap-4 rounded-lg border border-black/10 p-4 hover:bg-black/5 dark:border-white/20 dark:hover:bg-white/10"
                                >
                                    <span>
                                        <span className="block font-medium">
                                            {lesson.number}. {lesson.title}
                                        </span>
                                        <span className="block text-sm opacity-70">{lesson.goal}</span>
                                    </span>
                                    <ReviewBadge status={lesson.review_status} />
                                </Link>
                            </li>
                        ))}
                    </ul>
                </section>
            ))}
        </div>
    );
}