/**
 * Illustration of an open book on a stand, softly lit.
 * It shows no readable verses: Qur'anic text is never used as decoration.
 * The glow animation lives in globals.css (.hero-glow).
 */
export default function HeroBook() {
    return (
        <svg
            viewBox="0 0 420 380"
            role="img"
            aria-label="Illustration of an open book on a wooden stand, softly lit"
            className="mx-auto w-full max-w-md"
        >
            <defs>
                <radialGradient id="hero-glow-gradient" cx="50%" cy="45%" r="55%">
                    <stop offset="0" stopColor="#F2D98F" stopOpacity="0.85" />
                    <stop offset="1" stopColor="#F2D98F" stopOpacity="0" />
                </radialGradient>
            </defs>

            <circle
                className="hero-glow"
                cx="210"
                cy="170"
                r="170"
                fill="url(#hero-glow-gradient)"
            />

            {/* The stand */}
            <path
                d="M118 340 L210 238 L302 340"
                fill="none"
                strokeWidth="12"
                strokeLinecap="round"
                className="stroke-[#6b4a2b]"
            />

            {/* The thickness of the pages */}
            <path
                d="M70 256 Q140 236 208 262 L208 274 Q140 248 70 268 Z M350 256 Q280 236 212 262 L212 274 Q280 248 350 268 Z"
                className="fill-band"
            />

            {/* The two pages */}
            <path
                d="M70 120 Q140 100 208 128 L208 262 Q140 236 70 256 Z M350 120 Q280 100 212 128 L212 262 Q280 236 350 256 Z"
                className="fill-page stroke-line"
            />

            {/* Decorative borders, stars and abstract lines (no text) */}
            <g fill="none" className="stroke-gold" strokeWidth="1.5">
                <path d="M86 138 Q142 122 198 144 L198 246 Q142 226 86 240 Z M334 138 Q278 122 222 144 L222 246 Q278 226 334 240 Z" />
                <rect x="128" y="156" width="28" height="28" />
                <rect x="128" y="156" width="28" height="28" transform="rotate(45 142 170)" />
                <rect x="264" y="156" width="28" height="28" />
                <rect x="264" y="156" width="28" height="28" transform="rotate(45 278 170)" />
            </g>
            <path
                d="M106 204H180M106 216H180M106 228H160M240 204H314M240 216H314M240 228H294"
                strokeWidth="3"
                strokeLinecap="round"
                className="stroke-line"
            />
        </svg>
    );
}