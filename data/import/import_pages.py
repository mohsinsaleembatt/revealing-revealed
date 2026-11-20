"""Import the Mushaf's 604 page boundaries, derived from verified data
already in the database.

Run from the project root, after import_tanzil.py, with the virtual
environment active:
    python data/import/import_pages.py

Safe to run again: it replaces the stored boundaries each time.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "apps" / "api"))

from sqlalchemy import delete, func, select  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402

from app.database import engine  # noqa: E402
from app.models import Ayah, MushafPage, Surah  # noqa: E402
from tanzil_files import read_page_starts  # noqa: E402
from verify_tanzil_text import check_checksums, check_pages  # noqa: E402

EXPECTED_PAGES = 604
TOTAL_AYAHS = 6236


def find_ayah_id(session: Session, surah_number: int, ayah_number: int) -> int:
    """Turn a (surah, ayah) pair into that verse's id, or stop with a message."""
    ayah_id = session.scalar(
        select(Ayah.id)
        .join(Surah, Ayah.surah_id == Surah.id)
        .where(Surah.number == surah_number, Ayah.number == ayah_number)
    )
    if ayah_id is None:
        raise SystemExit(
            f"Verse {surah_number}:{ayah_number} does not exist. "
            "Run import_tanzil.py first."
        )
    return ayah_id


def main() -> int:
    page_starts = read_page_starts()
    problems = check_checksums() + check_pages(page_starts)
    if problems:
        print("The files did not pass their checks. Nothing was imported.")
        for problem in problems[:15]:
            print(f"  - {problem}")
        return 1

    with Session(engine) as session, session.begin():
        start_ids = [find_ayah_id(session, s, a) for s, a in page_starts]
        if start_ids != sorted(start_ids):
            raise SystemExit("Page start points are not in increasing order.")

        session.execute(delete(MushafPage))
        session.flush()

        # Each page ends right before the next starts; the last ends at the
        # final verse. This relies on verse ids running 1 to 6236 in order.
        end_ids = [*(start - 1 for start in start_ids[1:]), TOTAL_AYAHS]
        session.add_all(
            MushafPage(number=number, start_ayah_id=start_id,
                       end_ayah_id=end_id)
            for number, (start_id, end_id) in enumerate(zip(start_ids, end_ids), start=1)
        )

    with Session(engine) as session:
        count = session.scalar(select(func.count()).select_from(MushafPage))
        covered = session.scalar(
            select(func.sum(MushafPage.end_ayah_id - MushafPage.start_ayah_id + 1))
        )

    print(f"Imported {count} page boundaries.")
    if count == EXPECTED_PAGES and covered == TOTAL_AYAHS:
        print("OK: page boundaries cover all verses exactly once.")
        return 0
    print(
        f"PROBLEM: expected {EXPECTED_PAGES} pages covering {TOTAL_AYAHS} verses; "
        f"got {count} covering {covered}."
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
