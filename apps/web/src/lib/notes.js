import { useSyncExternalStore } from "react";

const STORAGE_KEY = "rr-notes-v1";
const CHANGE_EVENT = "rr-notes-changed";
export const MAX_NOTE_LENGTH = 2000;
const EMPTY = [];

// useSyncExternalStore needs the same array back until the data really changes,
// so the last reading is remembered here.
let cachedRaw = null;
let cachedNotes = EMPTY;

/** True if a stored item has the shape we expect. */
function isValidNote(note) {
    return (
        note !== null &&
        typeof note === "object" &&
        typeof note.id === "string" &&
        Number.isInteger(note.surah) &&
        Number.isInteger(note.ayah) &&
        typeof note.surahName === "string" &&
        typeof note.text === "string" &&
        typeof note.createdAt === "string" &&
        typeof note.updatedAt === "string"
    );
}

/** Read all notes from this browser. Anything malformed is ignored. */
function readNotes() {
    let raw = null;
    try {
        raw = window.localStorage.getItem(STORAGE_KEY);
    } catch {
        return cachedNotes; // storage is blocked: keep what we have in memory
    }
    if (raw === cachedRaw) return cachedNotes;

    cachedRaw = raw;
    try {
        const parsed = raw ? JSON.parse(raw) : EMPTY;
        cachedNotes = Array.isArray(parsed) ? parsed.filter(isValidNote) : EMPTY;
    } catch {
        cachedNotes = EMPTY;
    }
    return cachedNotes;
}

/**
 * Save all notes. Returns true if they were stored in this browser, false if
 * storage is blocked or full (the notes then last only for this visit).
 */
function writeNotes(next) {
    let stored = true;
    try {
        window.localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
    } catch {
        cachedNotes = next;
        cachedRaw = null;
        stored = false;
    }
    window.dispatchEvent(new Event(CHANGE_EVENT));
    return stored;
}

function subscribe(callback) {
    window.addEventListener("storage", callback); // changes from another tab
    window.addEventListener(CHANGE_EVENT, callback); // changes from this tab
    return () => {
        window.removeEventListener("storage", callback);
        window.removeEventListener(CHANGE_EVENT, callback);
    };
}

const subscribeNothing = () => () => { };

/**
 * React hook: the current notes, and whether they have been read yet.
 * On the server (and during the first draw) there are no notes and ready is false.
 */
export function useNotes() {
    const notes = useSyncExternalStore(subscribe, readNotes, () => EMPTY);
    const ready = useSyncExternalStore(subscribeNothing, () => true, () => false);
    return { notes, ready };
}

/** Sort by surah, then verse, then creation time. */
export function compareNotes(a, b) {
    return (
        a.surah - b.surah ||
        a.ayah - b.ayah ||
        a.createdAt.localeCompare(b.createdAt)
    );
}

function cleanText(text) {
    return String(text).trim().slice(0, MAX_NOTE_LENGTH);
}

/** Add a note. Returns true if it was stored in this browser. */
export function addNote({ surah, ayah, surahName, text }) {
    const now = new Date().toISOString();
    return writeNotes([
        ...readNotes(),
        {
            id: crypto.randomUUID(),
            surah,
            ayah,
            surahName,
            text: cleanText(text),
            createdAt: now,
            updatedAt: now,
        },
    ]);
}

/** Change the text of a note. Returns true if it was stored in this browser. */
export function updateNote(id, text) {
    const now = new Date().toISOString();
    return writeNotes(
        readNotes().map((note) =>
            note.id === id ? { ...note, text: cleanText(text), updatedAt: now } : note
        )
    );
}

/** Delete a note. Returns true if the change was stored in this browser. */
export function deleteNote(id) {
    return writeNotes(readNotes().filter((note) => note.id !== id));
}

/** All notes as a Markdown document. */
export function notesToMarkdown(notes) {
    const lines = [
        "# My notes (Revealing Revealed)",
        "",
        `Exported ${new Date().toISOString().slice(0, 10)}`,
        "",
    ];
    for (const note of [...notes].sort(compareNotes)) {
        lines.push(`## ${note.surahName} ${note.surah}:${note.ayah}`, "", note.text, "");
    }
    return lines.join("\n");
}

/** All notes as JSON, so they can be kept or imported somewhere else later. */
export function notesToJson(notes) {
    return JSON.stringify({ version: 1, notes: [...notes].sort(compareNotes) }, null, 2);
}

/** Offer a text file to download. */
export function downloadFile(filename, content, mimeType) {
    const url = URL.createObjectURL(new Blob([content], { type: mimeType }));
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
}