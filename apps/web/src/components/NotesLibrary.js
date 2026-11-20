"use client";

import { useState } from "react";
import Link from "next/link";

import {
    compareNotes,
    deleteNote,
    downloadFile,
    notesToJson,
    notesToMarkdown,
    useNotes,
} from "@/lib/notes";

function formatDate(isoString) {
    return new Date(isoString).toLocaleDateString("en-GB", {
        day: "numeric",
        month: "short",
        year: "numeric",
    });
}

/** Every note, with search and export. */
export default function NotesLibrary() {
    const { notes, ready } = useNotes();
    const [query, setQuery] = useState("");

    const needle = query.trim().toLowerCase();
    const shown = [...notes].sort(compareNotes).filter(
        (note) =>
            !needle ||
            note.text.toLowerCase().includes(needle) ||
            note.surahName.toLowerCase().includes(needle) ||
            `${note.surah}:${note.ayah}`.includes(needle)
    );

    function handleDelete(id) {
        if (window.confirm("Delete this note?")) deleteNote(id);
    }

    if (!ready) return <p className="mt-6 text-mute">Loading your notes…</p>;

    if (notes.length === 0) {
        return (
            <p className="mt-6 text-mute">
                You have no notes yet. Open a page of the{" "}
                <Link href="/quran/page/1" className="underline">
                    Qur&apos;an
                </Link>{" "}
                and select a verse number to write one.
            </p>
        );
    }

    return (
        <div className="mt-6">
            <div className="flex flex-wrap items-end gap-4">
                <div className="flex-1">
                    <label htmlFor="note-search" className="block font-semibold">
                        Search your notes
                    </label>
                    <input
                        id="note-search"
                        type="search"
                        value={query}
                        onChange={(event) => setQuery(event.target.value)}
                        placeholder="A word, a surah name, or a reference like 2:255"
                        className="mt-1 w-full rounded border border-line bg-paper p-2"
                    />
                </div>
                <button
                    type="button"
                    onClick={() =>
                        downloadFile("my-notes.md", notesToMarkdown(notes), "text/markdown")
                    }
                    className="rounded-lg border border-accent px-4 py-2 font-semibold text-accent"
                >
                    Export as Markdown
                </button>
                <button
                    type="button"
                    onClick={() =>
                        downloadFile("my-notes.json", notesToJson(notes), "application/json")
                    }
                    className="rounded-lg border border-accent px-4 py-2 font-semibold text-accent"
                >
                    Export as JSON
                </button>
            </div>

            <p className="mt-3 text-sm text-mute" role="status">
                {shown.length} of {notes.length} notes
            </p>

            <ul className="mt-4 space-y-3">
                {shown.map((note) => (
                    <li key={note.id} className="rounded-lg border border-line bg-raised p-4">
                        <p className="font-semibold">
                            {note.surahName} {note.surah}:{note.ayah}
                            <span className="ml-3 text-sm font-normal text-mute">
                                {formatDate(note.updatedAt)}
                            </span>
                        </p>
                        <p className="mt-2 whitespace-pre-line">{note.text}</p>
                        <p className="mt-3 flex gap-5 text-sm">
                            <Link
                                href={`/surah/${note.surah}#ayah-${note.ayah}`}
                                className="underline"
                            >
                                Open the verse
                            </Link>
                            <button type="button" onClick={() => handleDelete(note.id)} className="underline">
                                Delete
                            </button>
                        </p>
                    </li>
                ))}
            </ul>
        </div>
    );
}