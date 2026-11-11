"""Read the files downloaded from Tanzil. Reading only; nothing is changed."""

import ast
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIR = ROOT / "data" / "sources" / "tanzil"
TEXT_FILE = SOURCE_DIR / "quran-uthmani.txt"
METADATA_FILE = SOURCE_DIR / "quran-data.js"
SOURCE_RECORD = SOURCE_DIR / "SOURCE.md"


def sha256_of(path: Path) -> str:
    """Return the SHA-256 fingerprint of a file."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def recorded_checksum(label: str) -> str | None:
    """Read a checksum written in SOURCE.md, for example the 'SHA-256' line."""
    for line in SOURCE_RECORD.read_text(encoding="utf-8").splitlines():
        if line.startswith(f"- {label}:"):
            return line.split(":", 1)[1].strip().lower()
    return None


def read_verses() -> list[tuple[int, int, str]]:
    """Return (surah, ayah, text) for each verse line, skipping the # notice."""
    verses = []
    # "utf-8-sig" also copes with an invisible byte-order mark at the start.
    with TEXT_FILE.open(encoding="utf-8-sig", newline="") as file:
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


def read_notice() -> str:
    """Return the copyright block (all lines starting with #), unchanged."""
    with TEXT_FILE.open(encoding="utf-8-sig", newline="") as file:
        lines = [line.rstrip("\r\n") for line in file if line.startswith("#")]
    return "\n".join(lines)


def read_surahs() -> list[dict]:
    """Read the surah list from quran-data.js.

    Each surah row is: [start, ayas, order, rukus, name, tname, ename, type].
    The first row of the array is empty and the last row is an end marker
    (the start position after the final verse); neither is a surah.
    """
    lines = METADATA_FILE.read_text(encoding="utf-8-sig").splitlines()
    first = next(
        i for i, line in enumerate(lines) if line.startswith("QuranData.Sura = [")
    )

    rows_text = []
    for line in lines[first + 1:]:
        stripped = line.strip()
        if stripped.startswith("];"):
            break
        if stripped and not stripped.startswith("//"):
            rows_text.append(stripped)

    # literal_eval reads Python-style data and never runs code.
    rows = [row for row in ast.literal_eval(
        "[" + "\n".join(rows_text) + "]") if row]

    # Set the end marker aside; it is checked against the verse total below.
    end_marker = rows.pop() if len(rows[-1]) == 2 else None

    surahs = []
    for number, row in enumerate(rows, start=1):
        # Each surah row must have exactly 8 fields. If not, stop and say where.
        if len(row) != 8:
            raise ValueError(
                f"Row {number} has {len(row)} fields instead of 8; "
                f"its first fields are {row[:4]}"
            )
        surahs.append(
            {
                "number": number,
                "start": row[0],
                "ayah_count": row[1],
                "name_arabic": row[4],
                "name_transliteration": row[5],
                "name_english": row[6],
                "revelation_place": row[7],
            }
        )

    total_verses = sum(surah["ayah_count"] for surah in surahs)
    if end_marker is not None and end_marker[0] != total_verses:
        raise ValueError(
            f"End marker says {end_marker[0]} verses but the surahs add up to "
            f"{total_verses}"
        )
    return surahs


def read_metadata_notice() -> str:
    """Return the comment header at the top of quran-data.js, unchanged."""
    notice = []
    for line in METADATA_FILE.read_text(encoding="utf-8-sig").splitlines():
        if line.startswith("//"):
            notice.append(line)
        elif notice:
            break  # the header ends at the first line that is not a comment
    return "\n".join(notice)
