/**
 * Ask the backend whether it is running.
 * Returns an object like { status: "ok" }, or null if the backend is unreachable.
 */
async function getBackendHealth() {
  const baseUrl = process.env.API_URL ?? "http://127.0.0.1:8000";

  try {
    const response = await fetch(`${baseUrl}/health`, { cache: "no-store" });
    if (!response.ok) return null;
    return await response.json();
  } catch {
    return null;
  }
}

export default async function Home() {
  const health = await getBackendHealth();

  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-4 p-8">
      <h1 className="text-3xl font-semibold">Revealing Revealed</h1>
      <p>Backend status: {health ? health.status : "unreachable"}</p>
    </main>
  );
}