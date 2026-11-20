"""Import the Mushaf's 30 juz boundaries, derived from verified data
already in the database.

Run from the project root, after import_tanzil.py, with the virtual
environment active:
    python data/import/import_juz.py

Safe to run again: it replaces the stored boundaries each time.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "apps" / "api"))

from sqlalchemy import delete, func, select  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402

from app.database import engine  # noqa: E402
from app.models import Ayah, Juz, Surah  # noqa: E402
from tanzil_files import read_juz_starts  # noqa: E402
from verify_tanzil_text import check_checksums, check_juz  # noqa: E402

EXPECTED_JUZ = 30
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
    juz_starts = read_juz_starts()
    problems = check_checksums() + check_juz(juz_starts)
    if problems:
        print("The files did not pass their checks. Nothing was imported.")
        for problem in problems[:15]:
            print(f"  - {problem}")
        return 1

    with Session(engine) as session, session.begin():
        start_ids = [find_ayah_id(session, surah, ayah)
                     for surah, ayah in juz_starts]
        if start_ids != sorted(start_ids):
            raise SystemExit("Juz start points are not in increasing order.")

        session.execute(delete(Juz))
        session.flush()

        # Each juz ends right before the next one starts; the last ends at
        # the final verse. This assumes ayah ids run 1 to 6236 with no gaps
        # in Qur'an order, which holds for a fresh import (see import_tanzil.py).
        end_ids = [*(start - 1 for start in start_ids[1:]), TOTAL_AYAHS]
        session.add_all(
            Juz(number=number, start_ayah_id=start_id, end_ayah_id=end_id)
            for number, (start_id, end_id) in enumerate(zip(start_ids, end_ids), start=1)
        )

    with Session(engine) as session:
        count = session.scalar(select(func.count()).select_from(Juz))
        covered = session.scalar(
            select(func.sum(Juz.end_ayah_id - Juz.start_ayah_id + 1)))

    print(f"Imported {count} juz boundaries.")
    if count == EXPECTED_JUZ and covered == TOTAL_AYAHS:
        print("OK: juz boundaries cover all verses exactly once.")
        return 0
    print(
        f"PROBLEM: expected {EXPECTED_JUZ} juz covering {TOTAL_AYAHS} verses; "
        f"got {count} covering {covered}."
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
