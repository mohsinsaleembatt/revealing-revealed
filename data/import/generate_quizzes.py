"""Generate quiz questions for lessons from the verified Qur'an data.

Run from the project root, with the virtual environment active, after
importing lessons:
    python data/import/generate_quizzes.py

Each lesson's questions are replaced by freshly generated ones. The random
choice of wrong options is seeded from the lesson, so the same input always
gives the same questions.

Note: once learners' answers are saved (a later phase), questions must be
versioned instead of replaced.
"""

import random
import sys
from pathlib import Path

# Make the API's code (app/database.py and app/models.py) importable from here.
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "apps" / "api"))

# These imports must come after the path line above, hence the noqa markers.
from sqlalchemy import func, select  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402

from app.database import engine  # noqa: E402
from app.models import (  # noqa: E402
    Ayah,
    Lesson,
    LessonBlock,
    QuizOption,
    QuizQuestion,
    Surah,
)

WRONG_OPTIONS = 3  # plus the correct answer makes 4 choices


def surah_label(surah: Surah) -> str:
    """Readable name used in prompts and options, e.g. 'Al-Faatiha (The Opening)'."""
    return f"{surah.name_transliteration} ({surah.name_english})"


def shuffled_options(rng: random.Random, correct: str, wrong: list[str]) -> list[QuizOption]:
    """Mix the correct and wrong answers into numbered options."""
    texts = [correct, *wrong]
    rng.shuffle(texts)
    return [
        QuizOption(position=position, text=text, is_correct=(text == correct))
        for position, text in enumerate(texts, start=1)
    ]


def make_questions(
    session: Session,
    lesson: Lesson,
    ayah: Ayah,
    surahs: list[Surah],
    rng: random.Random,
) -> list[QuizQuestion]:
    """Build the questions for one verse block of a lesson."""
    surah = ayah.surah
    others = [other for other in surahs if other.id != surah.id]
    questions = []

    # Question type 1: which surah is this verse from?
    # Skipped when the same verse text occurs elsewhere: it would have two answers.
    same_text = session.scalar(
        select(func.count()).select_from(Ayah).where(
            Ayah.text_uthmani == ayah.text_uthmani)
    )
    if same_text == 1:
        wrong = rng.sample(others, WRONG_OPTIONS)
        questions.append(
            QuizQuestion(
                lesson_id=lesson.id,
                ayah_id=ayah.id,
                question_type="verse_surah",
                prompt="Which surah is this verse from?",
                explanation=(
                    f"This is verse {ayah.number} of Surah {surah_label(surah)}, "
                    "according to the verified Tanzil text."
                ),
                options=shuffled_options(
                    rng, surah_label(surah), [surah_label(s) for s in wrong]
                ),
            )
        )
    else:
        print(f"  Note: verse {surah.number}:{ayah.number} repeats elsewhere; "
              "the 'which surah' question was skipped.")

    # Question type 2: how many verses does this surah have?
    other_counts = sorted(
        {s.ayah_count for s in others if s.ayah_count != surah.ayah_count})
    wrong_counts = rng.sample(other_counts, WRONG_OPTIONS)
    questions.append(
        QuizQuestion(
            lesson_id=lesson.id,
            question_type="surah_ayah_count",
            prompt=f"How many verses does Surah {surah_label(surah)} have?",
            explanation=(
                f"Surah {surah_label(surah)} has {surah.ayah_count} verses, "
                "according to the verified Tanzil metadata."
            ),
            options=shuffled_options(
                rng, str(surah.ayah_count), [str(count)
                                             for count in wrong_counts]
            ),
        )
    )
    return questions


def main() -> int:
    with Session(engine) as session, session.begin():
        surahs = list(session.scalars(select(Surah).order_by(Surah.number)))

        for lesson in session.scalars(select(Lesson).order_by(Lesson.id)):
            # Replace this lesson's old questions (options are deleted with them).
            for old in session.scalars(
                select(QuizQuestion).where(QuizQuestion.lesson_id == lesson.id)
            ).all():
                session.delete(old)
            session.flush()

            verse_blocks = session.scalars(
                select(LessonBlock)
                .where(LessonBlock.lesson_id == lesson.id, LessonBlock.kind == "ayah")
                .order_by(LessonBlock.position)
            ).all()

            created = []
            for block in verse_blocks:
                ayah = session.get(Ayah, block.ayah_id)
                rng = random.Random(
                    f"{lesson.slug}-{block.position}-{ayah.id}")
                created.extend(make_questions(
                    session, lesson, ayah, surahs, rng))
            session.add_all(created)

            print(
                f"Lesson '{lesson.slug}': {len(created)} question(s) generated")
            if len(verse_blocks) < 2:
                print("  Note: fewer than 2 verse blocks; the mid-lesson check "
                      "will need more questions.")

    print("OK: quiz questions generated.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
