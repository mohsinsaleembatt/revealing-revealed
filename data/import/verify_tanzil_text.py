"""Check the downloaded Tanzil files before they are imported.

The script only reads files and prints a report. It changes nothing.
Run it from the project root:  python data/import/verify_tanzil_text.py
"""

import sys
from collections import Counter

from tanzil_files import (
    METADATA_FILE,
    TEXT_FILE,
    read_surahs,
    read_verses,
    recorded_checksum,
    sha256_of,
)

EXPECTED_SURAHS = 114
EXPECTED_AYAHS = 6236


def is_arabic_character(character: str) -> bool:
    """True for letters and marks of the main Arabic Unicode block, or a space."""
    return "\u0600" <= character <= "\u06ff" or character == " "


def check_checksums() -> list[str]:
    """Compare each downloaded file with the checksum recorded in SOURCE.md."""
    problems = []
    for path, label in ((TEXT_FILE, "SHA-256"), (METADATA_FILE, "Metadata SHA-256")):
        recorded = recorded_checksum(label)
        if recorded is None:
            problems.append(f"No '- {label}:' line found in SOURCE.md")
        elif recorded != sha256_of(path):
            problems.append(f"{path.name}: checksum differs from SOURCE.md")
    return problems


def check_verses(verses: list[tuple[int, int, str]]) -> list[str]:
    """Check numbering and totals."""
    problems = []
    previous = (0, 0)
    for surah, ayah, text in verses:
        starts_next_surah = surah == previous[0] + 1 and ayah == 1
        continues_surah = surah == previous[0] and ayah == previous[1] + 1
        if not (starts_next_surah or continues_surah):
            problems.append(f"Unexpected order at {surah}:{ayah}")
        if not text.strip():
            problems.append(f"Empty text at {surah}:{ayah}")
        previous = (surah, ayah)

    if len(verses) != EXPECTED_AYAHS:
        problems.append(
            f"Found {len(verses)} verses, expected {EXPECTED_AYAHS}")
    return problems


def check_verse_characters(verses: list[tuple[int, int, str]]) -> list[str]:
    """Report characters in the verse text that are outside the Arabic blocks.

    Characters are shown as code points (U+XXXX), not as glyphs, so the report
    reads the same in any terminal.
    """
    arabic_ranges = (
        ("\u0600", "\u06ff"),  # Arabic
        ("\u0750", "\u077f"),  # Arabic Supplement
        ("\u08a0", "\u08ff"),  # Arabic Extended-A
    )
    unusual = Counter()
    for _, _, text in verses:
        for character in text:
            in_arabic = any(low <= character <= high for low,
                            high in arabic_ranges)
            if not in_arabic and character != " ":
                unusual[character] += 1

    return [
        f"Verse text contains U+{ord(character):04X} ({count} times); please review"
        for character, count in unusual.items()
    ]


def check_surahs(surahs: list[dict], verses: list[tuple[int, int, str]]) -> list[str]:
    """Check the metadata against the verse text and against itself."""
    problems = []
    if len(surahs) != EXPECTED_SURAHS:
        problems.append(
            f"Found {len(surahs)} surahs, expected {EXPECTED_SURAHS}")

    verse_counts = Counter(surah for surah, _, _ in verses)
    expected_start = 0
    for entry in surahs:
        number = entry["number"]
        if entry["ayah_count"] != verse_counts[number]:
            problems.append(
                f"Surah {number}: verse count differs from the text file")
        if entry["start"] != expected_start:
            problems.append(
                f"Surah {number}: start position is not continuous")
        expected_start += entry["ayah_count"]
        if entry["revelation_place"] not in ("Meccan", "Medinan"):
            problems.append(f"Surah {number}: unexpected revelation place")
        if not all(is_arabic_character(c) for c in entry["name_arabic"]):
            problems.append(
                f"Surah {number}: Arabic name has non-Arabic characters")
        if not entry["name_transliteration"] or not entry["name_english"]:
            problems.append(f"Surah {number}: a name is empty")
    return problems


def main() -> int:
    verses = read_verses()
    surahs = read_surahs()

    problems = (
        check_checksums()
        + check_verses(verses)
        + check_verse_characters(verses)
        + check_surahs(surahs, verses)
    )

    print(f"Verses read: {len(verses)}")
    print(f"Surahs read: {len(surahs)}")
    if problems:
        print("PROBLEMS FOUND:")
        for problem in problems[:15]:
            print(f"  - {problem}")
        return 1
    print("OK: checksums match, numbering is continuous, counts agree.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
