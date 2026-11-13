"use client";

/** Switch between the light and dark themes and remember the choice. */
export default function ThemeToggle() {
    function toggle() {
        const root = document.documentElement;
        const next = root.dataset.theme === "dark" ? "light" : "dark";
        root.dataset.theme = next;
        try {
            localStorage.setItem("theme", next);
        } catch {
            // Storage can be blocked; the theme then lasts only for this visit.
        }
    }

    return (
        <button
            type="button"
            onClick={toggle}
            className="rounded-lg border border-line px-3 py-1.5 text-sm hover:bg-band"
        >
            <span className="only-light">Dark theme</span>
            <span className="only-dark">Light theme</span>
        </button>
    );
}