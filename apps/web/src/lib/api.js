const API_URL = process.env.API_URL ?? "http://127.0.0.1:8000";

/**
 * Fetch JSON from the backend API.
 * @param {string} path - for example "/quran/surahs"
 * @param {{ fresh?: boolean }} [options] - fresh: true skips caching
 * @returns {Promise<object | null>} the data, or null if the API answers 404
 */
export async function apiGet(path, { fresh = false } = {}) {
    // The Qur'anic text never changes, so Next.js may reuse an answer for an hour.
    const response = await fetch(
        `${API_URL}${path}`,
        fresh ? { cache: "no-store" } : { next: { revalidate: 3600 } }
    );
    if (response.status === 404) return null;
    if (!response.ok) {
        throw new Error(`API error ${response.status} for ${path}`);
    }
    return response.json();
}

/**
 * Send JSON to the backend API and return its JSON answer.
 * @param {string} path
 * @param {object} body
 * @returns {Promise<object>}
 */
export async function apiPost(path, body) {
    const response = await fetch(`${API_URL}${path}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
        cache: "no-store",
    });
    if (!response.ok) {
        throw new Error(`API error ${response.status} for ${path}`);
    }
    return response.json();
}