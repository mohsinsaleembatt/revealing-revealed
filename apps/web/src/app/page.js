import Link from "next/link";

export default function Home() {
  return (
    <div className="py-12">
      <h1 className="font-serif text-4xl font-semibold">Revealing Revealed</h1>
      <p className="mt-3 max-w-xl text-lg text-mute">
        The new home page arrives in the next step. For now:
      </p>
      <p className="mt-6 flex flex-wrap gap-4">
        <Link
          href="/quran"
          className="rounded-lg bg-accent px-5 py-3 font-semibold text-accent-ink"
        >
          Open the Qur&apos;an
        </Link>
        <Link
          href="/learn"
          className="rounded-lg border border-accent px-5 py-3 font-semibold text-accent"
        >
          Start learning
        </Link>
      </p>
    </div>
  );
}