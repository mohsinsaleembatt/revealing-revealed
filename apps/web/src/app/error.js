"use client";

export default function Error({ reset }) {
    return (
        <div className="py-16 text-center">
            <h1 className="text-2xl font-semibold">Something went wrong</h1>
            <p className="mt-2 opacity-70">
                The server may be unavailable. Please try again.
            </p>
            <button
                onClick={reset}
                className="mt-6 rounded-lg border border-black/20 px-4 py-2 dark:border-white/30"
            >
                Try again
            </button>
        </div>
    );
}