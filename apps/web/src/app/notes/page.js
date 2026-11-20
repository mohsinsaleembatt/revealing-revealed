import NotesLibrary from "@/components/NotesLibrary";

export const metadata = { title: "My notes | Revealing Revealed" };

export default function NotesPage() {
    return (
        <div className="container-reading">
            <h1 className="font-serif text-3xl font-semibold">My notes</h1>
            <p className="mt-2 text-mute">
                Your notes are saved only in this browser, on this device. Clearing your
                browser&apos;s site data deletes them, so export a copy now and then.
                When accounts arrive, they will be able to keep notes on every device.
            </p>
            <NotesLibrary />
        </div>
    );
}