"use client";

import { useState } from "react";

import { checkAnswer } from "@/app/learn/actions";
import { quranFont } from "@/lib/fonts";

/**
 * Multiple-choice quiz. The correct answers stay on the server until the
 * learner submits, and scores are not saved yet.
 * @param {{ questions: Array }} props
 */
export default function Quiz({ questions }) {
    const [selected, setSelected] = useState({}); // question id -> option id
    const [results, setResults] = useState(null); // question id -> server result
    const [pending, setPending] = useState(false);
    const [error, setError] = useState("");

    const allAnswered = questions.every((q) => selected[q.id] !== undefined);
    const score = results
        ? Object.values(results).filter((result) => result.correct).length
        : 0;

    async function handleSubmit() {
        setPending(true);
        setError("");
        try {
            const pairs = await Promise.all(
                questions.map(async (q) => [q.id, await checkAnswer(q.id, selected[q.id])])
            );
            setResults(Object.fromEntries(pairs));
        } catch {
            setError("Could not check your answers. Please try again.");
        } finally {
            setPending(false);
        }
    }

    function handleReset() {
        setSelected({});
        setResults(null);
    }

    return (
        <div className="space-y-6">
            {questions.map((q, index) => {
                const result = results?.[q.id];
                return (
                    <fieldset
                        key={q.id}
                        disabled={results !== null}
                        className="rounded-lg border border-black/10 p-4 dark:border-white/20"
                    >
                        <legend className="px-1 font-medium">
                            {index + 1}. {q.prompt}
                        </legend>

                        {q.ayah_text && (
                            <p
                                dir="rtl"
                                lang="ar"
                                className={`${quranFont.className} my-3 text-3xl leading-[2.4]`}
                            >
                                {q.ayah_text}
                            </p>
                        )}

                        <div className="mt-2 space-y-2">
                            {q.options.map((option) => (
                                <label key={option.id} className="flex items-center gap-2">
                                    <input
                                        type="radio"
                                        name={`question-${q.id}`}
                                        value={option.id}
                                        checked={selected[q.id] === option.id}
                                        onChange={() => setSelected({ ...selected, [q.id]: option.id })}
                                    />
                                    <span>{option.text}</span>
                                    {result && option.id === result.correct_option_id && (
                                        <span className="text-sm">(correct answer)</span>
                                    )}
                                </label>
                            ))}
                        </div>

                        {result && (
                            <p className="mt-3 text-sm" role="status">
                                <strong>{result.correct ? "Correct." : "Not correct."}</strong>{" "}
                                {result.explanation}
                            </p>
                        )}
                    </fieldset>
                );
            })}

            {error && <p role="alert">{error}</p>}

            {results ? (
                <div className="space-y-3">
                    <p>
                        You answered {score} of {questions.length} correctly. Scores are not
                        saved yet.
                    </p>
                    <button
                        onClick={handleReset}
                        className="rounded-lg border border-black/20 px-4 py-2 dark:border-white/30"
                    >
                        Try again
                    </button>
                </div>
            ) : (
                <button
                    onClick={handleSubmit}
                    disabled={!allAnswered || pending}
                    className="rounded-lg border border-black/20 px-4 py-2 disabled:opacity-50 dark:border-white/30"
                >
                    {pending ? "Checking…" : "Check answers"}
                </button>
            )}
        </div>
    );
}