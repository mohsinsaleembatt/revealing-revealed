"use client";

import { Fragment, useState } from "react";
import Link from "next/link";

import { quranFont } from "@/lib/fonts";
import {
    MAX_NOTE_LENGTH,
    addNote,
    deleteNote,
    updateNote,
    useNotes,
} from "@/lib/notes";

const keyOf = (surah, ayah) => `${surah}:${ayah}`;

/**
 * One Mushaf page with a notes panel beside it.
 * @param {{ page: object }} props - the page data from the API
 */
export default function MushafPageReader({ page }) {
    const { notes, ready } = useNotes();
    const [selected, setSelected] = useState(null); // { surah, ayah } or null
    const [draft, setDraft] = useState("");
    const [editingId, setEditingId] = useState(null);
    const [warning, setWarning] = useState("");

    const surahByNumber = Object.fromEntries(
        page.surahs.map((surah) => [surah.number, surah])
    );
    const surahNames = page.surahs.map((s) => s.name_transliteration).join(" · ");

    // How many notes each verse has, and which notes belong to this page.
    const counts = new Map();
    for (const note of notes) {
        const key = keyOf(note.surah, note.ayah);
        counts.set(key, (counts.get(key) ?? 0) + 1);
    }
    const pageKeys = new Set(page.verses.map((v) => keyOf(v.surah_number, v.number)));
    const pageNotes = notes.filter((n) => pageKeys.has(keyOf(n.surah, n.ayah)));

    const selectedKey = selected ? keyOf(selected.surah, selected.ayah) : null;
    const verseNotes = notes.filter((n) => keyOf(n.surah, n.ayah) === selectedKey);

    function resetEditor() {
        setDraft("");
        setEditingId(null);
        setWarning("");
    }

    function selectVerse(surah, ayah) {
        resetEditor();
        setSelected(
            selected && keyOf(selected.surah, selected.ayah) === keyOf(surah, ayah)
                ? null
                : { surah, ayah }
        );
    }

    function handleSave() {
        if (!draft.trim()) {
            setWarning("Write something first.");
            return;
        }
        const stored = editingId
            ? updateNote(editingId, draft)
            : addNote({
                surah: selected.surah,
                ayah: selected.ayah,
                surahName: surahByNumber[selected.surah].name_transliteration,
                text: draft,
            });
        setDraft("");
        setEditingId(null);
        setWarning(
            stored
                ? ""
                : "Your browser blocked saving, so this note will be lost when you leave. Use Export to keep a copy."
        );
    }

    function handleEdit(note) {
        setEditingId(note.id);
        setDraft(note.text);
        setWarning("");
    }

    function handleDelete(id) {
        if (window.confirm("Delete this note?")) {
            deleteNote(id);
            if (editingId === id) resetEditor();
        }
    }

    return (
        <div className="grid gap-8 lg:grid-cols-[minmax(0,36rem)_minmax(0,20rem)] lg:justify-center">
            <div>
                <article
                    className="relative aspect-[1/1.414] w-full rounded-sm border border-line bg-page px-8 py-10 shadow-lg sm:px-12"
                    aria-label={`Mushaf page ${page.number}`}
                >
                    <div
                        aria-hidden="true"
                        className="pointer-events-none absolute inset-3 border border-gold"
                    />

                    <header className="relative flex justify-between text-sm text-mute">
                        <span>{surahNames}</span>
                        <span>{page.juz_number ? `Juz ${page.juz_number}` : ""}</span>
                    </header>

                    <div
                        dir="rtl"
                        lang="ar"
                        className={`${quranFont.className} relative mt-8 text-2xl leading-[2.5] sm:text-3xl`}
                        style={{ textAlign: "justify" }}
                    >
                        {page.verses.map((verse) => {
                            const key = keyOf(verse.surah_number, verse.number);
                            const isSelected = key === selectedKey;
                            const count = counts.get(key) ?? 0;
                            return (
                                <Fragment key={key}>
                                    {verse.number === 1 && (
                                        <div className="my-4 rounded-sm border border-gold py-1 text-center">
                                            {surahByNumber[verse.surah_number].name_arabic}
                                        </div>
                                    )}
                                    <span
                                        id={`ayah-${verse.surah_number}-${verse.number}`}
                                        className={`rounded ${isSelected ? "bg-band" : ""} ${count
                                                ? "underline decoration-gold decoration-dotted underline-offset-[10px]"
                                                : ""
                                            }`}
                                    >
                                        {verse.text_uthmani}
                                    </span>{" "}
                                    <button
                                        type="button"
                                        onClick={() => selectVerse(verse.surah_number, verse.number)}
                                        aria-pressed={isSelected}
                                        aria-label={`Verse ${verse.number}: ${count ? `${count} ${count === 1 ? "note" : "notes"}` : "add a note"
                                            }`}
                                        className={`mx-1 inline-block min-w-7 rounded-full border px-1 text-center font-sans text-sm ${count
                                                ? "border-accent bg-accent text-accent-ink"
                                                : "border-current opacity-80 hover:opacity-100"
                                            } ${isSelected ? "ring-2 ring-accent ring-offset-2 ring-offset-page" : ""}`}
                                    >
                                        {verse.number.toLocaleString("ar-EG")}
                                    </button>{" "}
                                </Fragment>
                            );
                        })}
                    </div>

                    <footer className="relative mt-8 text-center text-sm text-mute">
                        {page.number}
                    </footer>
                </article>

                <nav aria-label="Page navigation" className="mt-6 flex justify-between text-sm">
                    {page.number < 604 ? (
                        <Link href={`/quran/page/${page.number + 1}`} className="underline">
                            ← Next page
                        </Link>
                    ) : (
                        <span />
                    )}
                    {page.number > 1 ? (
                        <Link href={`/quran/page/${page.number - 1}`} className="underline">
                            Previous page →
                        </Link>
                    ) : (
                        <span />
                    )}
                </nav>
            </div>

            <aside
                aria-label="Notes"
                className="rounded-lg border border-line bg-raised p-4 text-sm lg:sticky lg:top-4 lg:self-start"
            >
                <h2 className="font-serif text-xl font-semibold">My notes</h2>
                <p className="mt-1 text-mute">
                    Saved only in this browser.{" "}
                    <Link href="/notes" className="underline">
                        All notes and export
                    </Link>
                </p>

                {selected ? (
                    <div className="mt-4">
                        <h3 className="font-semibold">
                            {surahByNumber[selected.surah].name_transliteration} {selected.surah}:
                            {selected.ayah}
                        </h3>

                        {verseNotes.length > 0 && (
                            <ul className="mt-2 space-y-2">
                                {verseNotes.map((note) => (
                                    <li key={note.id} className="rounded border border-line p-3">
                                        <p className="whitespace-pre-line">{note.text}</p>
                                        <p className="mt-2 flex gap-4">
                                            <button type="button" onClick={() => handleEdit(note)} className="underline">
                                                Edit
                                            </button>
                                            <button type="button" onClick={() => handleDelete(note.id)} className="underline">
                                                Delete
                                            </button>
                                        </p>
                                    </li>
                                ))}
                            </ul>
                        )}

                        <label htmlFor="note-text" className="mt-4 block font-semibold">
                            {editingId ? "Edit note" : "New note"}
                        </label>
                        <textarea
                            id="note-text"
                            value={draft}
                            onChange={(event) => setDraft(event.target.value)}
                            maxLength={MAX_NOTE_LENGTH}
                            rows={4}
                            className="mt-1 w-full rounded border border-line bg-paper p-2"
                        />
                        <p className="mt-1 text-xs text-mute">
                            {draft.length} / {MAX_NOTE_LENGTH}
                        </p>

                        <p className="mt-3 flex gap-3">
                            <button
                                type="button"
                                onClick={handleSave}
                                className="rounded-lg bg-accent px-4 py-2 font-semibold text-accent-ink"
                            >
                                Save note
                            </button>
                            <button
                                type="button"
                                onClick={() => {
                                    resetEditor();
                                    setSelected(null);
                                }}
                                className="rounded-lg border border-line px-4 py-2"
                            >
                                Close
                            </button>
                        </p>
                    </div>
                ) : (
                    <div className="mt-4">
                        <p className="text-mute">Select a verse number to add or read a note.</p>
                        {ready && pageNotes.length > 0 && (
                            <ul className="mt-3 space-y-2">
                                {pageNotes.map((note) => (
                                    <li key={note.id}>
                                        <button
                                            type="button"
                                            onClick={() => selectVerse(note.surah, note.ayah)}
                                            className="w-full rounded border border-line p-3 text-start hover:bg-band"
                                        >
                                            <span className="font-semibold">
                                                {note.surahName} {note.surah}:{note.ayah}
                                            </span>
                                            <span className="mt-1 block text-mute">
                                                {note.text.length > 90 ? `${note.text.slice(0, 90)}…` : note.text}
                                            </span>
                                        </button>
                                    </li>
                                ))}
                            </ul>
                        )}
                    </div>
                )}

                {warning && (
                    <p role="alert" className="mt-3 font-semibold">
                        {warning}
                    </p>
                )}
            </aside>
        </div>
    );
}