"""Import the verified Tanzil text and metadata into PostgreSQL.

Run from the project root, with the virtual environment active:
    python data/import/import_tanzil.py               import, then verify
    python data/import/import_tanzil.py --check-only  verify only

The text is stored exactly as downloaded. Nothing is edited.
"""

import argparse
import sys
from pathlib import Path

# Make the API's code (app/database.py and app/models.py) importable from here.
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "apps" / "api"))

# These imports must come after the path line above, hence the noqa markers.
from sqlalchemy import func, select, text  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402

from app.database import engine  # noqa: E402
from app.models import Ayah, Source, Surah  # noqa: E402
from tanzil_files import (  # noqa: E402
    METADATA_FILE,
    TEXT_FILE,
    read_metadata_notice,
    read_notice,
    read_surahs,
    read_verses,
    sha256_of,
)
from verify_tanzil_text import (  # noqa: E402
    check_checksums,
    check_surahs,
    check_verse_characters,
    check_verses,
)

TEXT_SOURCE = {
    "name": "Tanzil Quran Text (Uthmani)",
    "url": "https://tanzil.net/download",
    "licence": "Creative Commons Attribution 3.0",
    "version": "1.1",
}
METADATA_SOURCE = {
    "name": "Tanzil Quran Metadata",
    "url": "https://tanzil.net",
    "licence": "Creative Commons Attribution 3.0",
    "version": "1.0",
}


def load_checked_files() -> tuple[list[tuple[int, int, str]], list[dict]]:
    """Read both files and stop if any check fails."""
    verses = read_verses()
    surahs = read_surahs()
    problems = (
        check_checksums()
        + check_verses(verses)
        + check_verse_characters(verses)
        + check_surahs(surahs, verses)
    )
    if problems:
        print("The files did not pass their checks. Nothing was imported.")
        for problem in problems[:15]:
            print(f"  - {problem}")
        raise SystemExit(1)
    return verses, surahs


def require_utf8(session: Session) -> None:
    """Stop unless the database stores text as UTF-8."""
    encoding = session.execute(text("SHOW server_encoding")).scalar_one()
    if encoding != "UTF8":
        raise SystemExit(
            f"The database encoding is {encoding}, not UTF8. "
            "Arabic text could be stored wrongly, so nothing was imported."
        )


def import_all(verses: list[tuple[int, int, str]], surahs: list[dict]) -> None:
    """Insert the sources, surahs and verses in a single transaction."""
    with Session(engine) as session, session.begin():
        require_utf8(session)

        if session.scalar(select(func.count()).select_from(Surah)):
            raise SystemExit(
                "The database already contains surahs, so nothing was imported."
            )

        text_source = Source(
            **TEXT_SOURCE, notice=read_notice(), file_sha256=sha256_of(TEXT_FILE)
        )
        metadata_source = Source(
            **METADATA_SOURCE,
            notice=read_metadata_notice(),
            file_sha256=sha256_of(METADATA_FILE),
        )
        session.add_all([text_source, metadata_source])
        session.flush()  # gives both sources their ids

        surah_rows = [
            Surah(
                number=entry["number"],
                name_arabic=entry["name_arabic"],
                name_transliteration=entry["name_transliteration"],
                name_english=entry["name_english"],
                revelation_place=entry["revelation_place"],
                ayah_count=entry["ayah_count"],
                source_id=metadata_source.id,
            )
            for entry in surahs
        ]
        session.add_all(surah_rows)
        session.flush()  # gives every surah its id

        surah_id = {row.number: row.id for row in surah_rows}
        session.add_all(
            Ayah(
                surah_id=surah_id[surah_number],
                number=ayah_number,
                text_uthmani=verse_text,
                source_id=text_source.id,
            )
            for surah_number, ayah_number, verse_text in verses
        )
    print("Imported: 2 sources, surahs and verses saved.")


def verify_database(verses: list[tuple[int, int, str]], surahs: list[dict]) -> bool:
    """Compare what is stored in the database with the files, exactly."""
    ok = True
    with Session(engine) as session:
        stored_verses = [
            tuple(row)
            for row in session.execute(
                select(Surah.number, Ayah.number, Ayah.text_uthmani)
                .join(Ayah, Ayah.surah_id == Surah.id)
                .order_by(Surah.number, Ayah.number)
            )
        ]
        stored_surahs = [
            tuple(row)
            for row in session.execute(
                select(
                    Surah.number,
                    Surah.name_arabic,
                    Surah.name_transliteration,
                    Surah.name_english,
                    Surah.revelation_place,
                    Surah.ayah_count,
                ).order_by(Surah.number)
            )
        ]
        sources = {row.name: row for row in session.scalars(select(Source))}

    expected_surahs = [
        (
            entry["number"],
            entry["name_arabic"],
            entry["name_transliteration"],
            entry["name_english"],
            entry["revelation_place"],
            entry["ayah_count"],
        )
        for entry in surahs
    ]

    if stored_verses == verses:
        print(f"Verses: all {len(verses)} match the file exactly.")
    else:
        ok = False
        bad = next(
            (a, b) for a, b in zip(stored_verses, verses) if a != b
        ) if len(stored_verses) == len(verses) else None
        print(
            f"Verses: MISMATCH (stored {len(stored_verses)}, file {len(verses)})")
        if bad:
            print(f"  first difference at {bad[1][0]}:{bad[1][1]}")

    if stored_surahs == expected_surahs:
        print(f"Surahs: all {len(surahs)} match the file exactly.")
    else:
        ok = False
        print("Surahs: MISMATCH")

    text_source = sources.get(TEXT_SOURCE["name"])
    metadata_source = sources.get(METADATA_SOURCE["name"])
    if (
        text_source
        and text_source.notice == read_notice()
        and text_source.file_sha256 == sha256_of(TEXT_FILE)
        and metadata_source
        and metadata_source.notice == read_metadata_notice()
        and metadata_source.file_sha256 == sha256_of(METADATA_FILE)
    ):
        print("Sources: notices and checksums match the files.")
    else:
        ok = False
        print("Sources: MISMATCH")
    return ok


def main() -> int:
    parser = argparse.ArgumentParser(description="Import Tanzil data.")
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="do not import; only compare the database with the files",
    )
    arguments = parser.parse_args()

    verses, surahs = load_checked_files()
    if not arguments.check_only:
        import_all(verses, surahs)

    if verify_database(verses, surahs):
        print("OK: the database matches the verified files.")
        return 0
    print("PROBLEM: the database does not match the files.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
