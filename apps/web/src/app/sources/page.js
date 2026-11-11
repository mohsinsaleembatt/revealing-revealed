import { apiGet } from "@/lib/api";

export const metadata = { title: "Sources | Revealing Revealed" };

export default async function SourcesPage() {
    const sources = await apiGet("/quran/sources");

    return (
        <div>
            <h1 className="text-3xl font-semibold">Sources and notices</h1>
            <p className="mt-2 opacity-70">
                Every piece of content on this site comes from a named source. The
                notices below are reproduced exactly as provided.
            </p>

            {sources.map((source) => (
                <section key={source.name} className="mt-8">
                    <h2 className="text-xl font-semibold">{source.name}</h2>
                    <p className="mt-1">
                        <a
                            href={source.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="underline"
                        >
                            {source.url}
                        </a>
                        {" · "}
                        {source.licence}
                        {source.version ? ` · version ${source.version}` : ""}
                    </p>
                    <pre className="mt-3 overflow-x-auto whitespace-pre-wrap rounded-lg border border-black/10 p-4 text-xs dark:border-white/20">
                        {source.notice}
                    </pre>
                </section>
            ))}
        </div>
    );
}