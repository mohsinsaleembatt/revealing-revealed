import { Amiri_Quran } from "next/font/google";

/**
 * Font for Qur'anic text. Amiri Quran is open-licensed and supports the
 * Qur'anic marks. Next.js downloads it once and serves it from our own site.
 */
export const quranFont = Amiri_Quran({
    subsets: ["arabic"],
    weight: "400",
    display: "swap",
});