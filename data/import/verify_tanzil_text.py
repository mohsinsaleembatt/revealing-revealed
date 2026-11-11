"""Check the downloaded Tanzil text before it is imported.

The script only reads files and prints a report. It changes nothing.
Run it from anywhere:  python data/import/verify_tanzil_text.py
"""

import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIR = ROOT / "data" / "sources" / "tanzil"
TEXT_FILE = SOURCE_DIR / "quran-uthmani.txt"
SOURCE_RECORD = SOURCE_DIR / "SOURCE.md"

EXPECTED_SURAHS = 114
EXPECTED_AYAHS = 6236


def read_verses(path: Path) -> list[tuple[int, int, str]]:
    """Return (surah, ayah, text) for each verse line, skipping the # notice."""
    verses = []
    # "utf-8-sig" also copes with an invisible byte-order mark at the file start.
    with path.open(encoding="utf-8-sig", newline="") as file:
        for line_number, line in enumerate(file, start=1):
            line = line.rstrip("\r\n")
            if not line or line.startswith("#"):
                continue
            parts = line.split("|", 2)
            if len(parts) != 3:
                raise ValueError(
                    f"Line {line_number}: expected surah|ayah|text")
            surah, ayah, text = parts
            verses.append((int(surah), int(ayah), text))
    return verses


def recorded_checksum(record: Path) -> str | None:
    """Read the SHA-256 value written in SOURCE.md."""
    for line in record.read_text(encoding="utf-8").splitlines():
        if line.startswith("- SHA-256:"):
            return line.split(":", 1)[1].strip().lower()
    return None


def check_structure(verses: list[tuple[int, int, str]]) -> list[str]:
    """Check numbering and counts. Returns a list of problems (empty if fine)."""
    problems = []
    previous = (0, 0)
    surahs = set()

    for surah, ayah, text in verses:
        starts_next_surah = surah == previous[0] + 1 and ayah == 1
        continues_surah = surah == previous[0] and ayah == previous[1] + 1
        if not (starts_next_surah or continues_surah):
            problems.append(
                f"Unexpected order at {surah}:{ayah} (after {previous[0]}:{previous[1]})"
            )
        if not text.strip():
            problems.append(f"Empty text at {surah}:{ayah}")
        surahs.add(surah)
        previous = (surah, ayah)

    if len(surahs) != EXPECTED_SURAHS:
        problems.append(
            f"Found {len(surahs)} surahs, expected {EXPECTED_SURAHS}")
    if len(verses) != EXPECTED_AYAHS:
        problems.append(
            f"Found {len(verses)} verses, expected {EXPECTED_AYAHS}")
    return problems


def main() -> int:
    problems = []

    actual = hashlib.sha256(TEXT_FILE.read_bytes()).hexdigest()
    recorded = recorded_checksum(SOURCE_RECORD)
    if recorded is None:
        problems.append("No '- SHA-256:' line found in SOURCE.md")
    elif recorded != actual:
        problems.append("Checksum differs from the one recorded in SOURCE.md")

    verses = read_verses(TEXT_FILE)
    problems.extend(check_structure(verses))

    print(f"Verses read: {len(verses)}")
    print(f"Checksum:    {actual}")
    if problems:
        print("PROBLEMS FOUND:")
        for problem in problems[:10]:
            print(f"  - {problem}")
        return 1
    print("OK: checksum matches, numbering is continuous, counts are correct.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
