"""Import lesson content (YAML files in content/) into PostgreSQL.

Run from the project root, with the virtual environment active:
    python data/import/import_lessons.py

Safe to run again: each lesson is replaced by what its file says.
Everything is saved in one transaction: if any file has a problem,
nothing is imported.
"""

import re
import sys
from pathlib import Path

import yaml

# Make the API's code (app/database.py and app/models.py) importable from here.
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "apps" / "api"))

# These imports must come after the path line above, hence the noqa markers.
from sqlalchemy import delete, select  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402

from app.database import engine  # noqa: E402
from app.models import Ayah, Lesson, LessonBlock, Module, Source, Surah  # noqa: E402

CONTENT_DIR = ROOT / "content" / "modules"
REVIEW_STATUSES = {"draft", "reviewed", "approved"}
BLOCK_KINDS = {"text", "ayah"}
VERSE_REFERENCE = re.compile(r"^(\d{1,3}):(\d{1,3})$")


class ContentError(Exception):
    """A problem in a content file. The message names the file."""


def read_yaml(path: Path) -> dict:
    """Read a YAML file. safe_load never runs code from the file."""
    with path.open(encoding="utf-8") as file:
        data = yaml.safe_load(file)
    if not isinstance(data, dict):
        raise ContentError(f"{path.name}: the file must contain named fields")
    return data


def require(data: dict, keys: list[str], where: str) -> None:
    """Stop if any of the listed fields is missing or empty."""
    for key in keys:
        if data.get(key) in (None, ""):
            raise ContentError(f"{where}: missing '{key}'")


def find_ayah_id(session: Session, reference: object, where: str) -> int:
    """Turn a reference such as "2:255" into the id of that verse."""
    match = VERSE_REFERENCE.match(str(reference))
    if match is None:
        raise ContentError(
            f"{where}: verse reference '{reference}' must look like \"2:255\" "
            "(in quotes)"
        )
    surah_number, ayah_number = (int(part) for part in match.groups())
    ayah_id = session.scalar(
        select(Ayah.id)
        .join(Surah, Ayah.surah_id == Surah.id)
        .where(Surah.number == surah_number, Ayah.number == ayah_number)
    )
    if ayah_id is None:
        raise ContentError(f"{where}: verse {reference} does not exist")
    return ayah_id


def find_source_id(session: Session, name: str, where: str) -> int:
    """Find a source in the source table by its exact name."""
    source_id = session.scalar(select(Source.id).where(Source.name == name))
    if source_id is None:
        raise ContentError(
            f"{where}: source '{name}' is not in the source table")
    return source_id


def build_block(
    session: Session, data: dict, position: int, status: str, where: str
) -> LessonBlock:
    """Check one block from a lesson file and build its database row."""
    kind = data.get("kind")
    if kind not in BLOCK_KINDS:
        raise ContentError(
            f"{where}: kind must be one of {sorted(BLOCK_KINDS)}")

    block = LessonBlock(position=position, kind=kind, note=data.get("note"))

    if kind == "text":
        require(data, ["body"], where)
        block.body = str(data["body"]).strip()
        if data.get("source"):
            block.source_id = find_source_id(session, data["source"], where)
            block.source_location = data.get("location")
        elif status != "draft":
            raise ContentError(
                f"{where}: a '{status}' lesson needs a source for every text block"
            )
    else:  # kind == "ayah"
        require(data, ["ref"], where)
        block.ayah_id = find_ayah_id(session, data["ref"], where)
    return block


def import_lesson(session: Session, module: Module, path: Path) -> str:
    """Create or update one lesson from its file. Returns the lesson's slug."""
    data = read_yaml(path)
    require(data, ["slug", "number", "title", "goal", "blocks"], path.name)

    status = data.get("review_status", "draft")
    if status not in REVIEW_STATUSES:
        raise ContentError(
            f"{path.name}: review_status must be one of {sorted(REVIEW_STATUSES)}")

    lesson = session.scalar(
        select(Lesson).where(Lesson.module_id ==
                             module.id, Lesson.slug == data["slug"])
    )
    if lesson is None:
        lesson = Lesson(module_id=module.id, slug=data["slug"])
        session.add(lesson)
    lesson.number = data["number"]
    lesson.title = data["title"]
    lesson.goal = data["goal"]
    lesson.review_status = status
    session.flush()  # gives a new lesson its id

    # Replace the old blocks with what the file says now.
    session.execute(delete(LessonBlock).where(
        LessonBlock.lesson_id == lesson.id))
    session.flush()

    for position, block_data in enumerate(data["blocks"], start=1):
        where = f"{path.name}, block {position}"
        block = build_block(session, block_data, position, status, where)
        block.lesson_id = lesson.id  # link the block to its lesson
        session.add(block)
    return lesson.slug


def import_module(session: Session, folder: Path) -> None:
    """Create or update one module and all of its lessons."""
    module_path = folder / "module.yaml"
    if not module_path.exists():
        raise ContentError(f"{folder.name}: module.yaml is missing")
    data = read_yaml(module_path)
    require(data, ["number", "slug", "title", "summary"],
            f"{folder.name}/module.yaml")

    module = session.scalar(select(Module).where(Module.slug == data["slug"]))
    if module is None:
        module = Module(slug=data["slug"])
        session.add(module)
    module.number = data["number"]
    module.title = data["title"]
    module.summary = data["summary"]
    session.flush()

    seen = [import_lesson(session, module, path)
            for path in sorted(folder.glob("lesson-*.yaml"))]
    print(
        f"Module {module.number} '{module.slug}': {len(seen)} lesson(s) imported")

    # Files are the source of truth, but we never delete lessons silently.
    stored = session.scalars(
        select(Lesson.slug).where(Lesson.module_id == module.id))
    for slug in stored:
        if slug not in seen:
            print(
                f"  Warning: lesson '{slug}' is in the database but has no file")


def main() -> int:
    folders = sorted(path for path in CONTENT_DIR.iterdir() if path.is_dir())
    try:
        # One transaction: an error anywhere undoes everything.
        with Session(engine) as session, session.begin():
            for folder in folders:
                import_module(session, folder)
    except ContentError as error:
        print(f"Nothing was imported. {error}")
        return 1
    print("OK: lesson content imported.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
