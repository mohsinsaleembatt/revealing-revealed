"""Read-only endpoints that serve modules and lessons."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.database import get_session
from app.models import Ayah, Lesson, LessonBlock, Module
from app.schemas import BlockOut, LessonDetail, ModuleOut

from app.models import Ayah, Lesson, LessonBlock, Module, QuizQuestion
from app.schemas import (
    AnswerIn,
    AnswerResult,
    BlockOut,
    LessonDetail,
    ModuleOut,
    OptionOut,
    QuestionOut,
)

router = APIRouter(prefix="/learn", tags=["learn"])

SessionDep = Annotated[Session, Depends(get_session)]


def block_to_schema(block: LessonBlock) -> BlockOut:
    """Turn a lesson block into what the API sends out.

    A verse block carries no text of its own: its text is read from the
    verified ayah table, exactly as stored.
    """
    data = {
        "position": block.position,
        "kind": block.kind,
        "body": block.body,
        "note": block.note,
    }
    if block.ayah is not None:
        data["ayah_reference"] = f"{block.ayah.surah.number}:{block.ayah.number}"
        data["ayah_text"] = block.ayah.text_uthmani
    if block.source is not None:
        data["source_name"] = block.source.name
        data["source_url"] = block.source.url
        data["source_location"] = block.source_location
    return BlockOut(**data)


@router.get("/modules")
def list_modules(session: SessionDep) -> list[ModuleOut]:
    """List all modules in order, each with its lessons."""
    modules = session.scalars(
        select(Module).options(selectinload(
            Module.lessons)).order_by(Module.number)
    )
    return list(modules)


@router.get("/modules/{module_slug}/lessons/{lesson_slug}")
def get_lesson(
    module_slug: str, lesson_slug: str, session: SessionDep
) -> LessonDetail:
    """Return one lesson with its blocks."""
    lesson = session.scalars(
        select(Lesson)
        .join(Module, Lesson.module_id == Module.id)
        .where(Module.slug == module_slug, Lesson.slug == lesson_slug)
        .options(
            selectinload(Lesson.module),
            selectinload(Lesson.blocks)
            .selectinload(LessonBlock.ayah)
            .selectinload(Ayah.surah),
            selectinload(Lesson.blocks).selectinload(LessonBlock.source),
        )
    ).one_or_none()
    if lesson is None:
        raise HTTPException(status_code=404, detail="Lesson not found")

    return LessonDetail(
        module_slug=lesson.module.slug,
        module_title=lesson.module.title,
        number=lesson.number,
        slug=lesson.slug,
        title=lesson.title,
        goal=lesson.goal,
        review_status=lesson.review_status,
        blocks=[block_to_schema(block) for block in lesson.blocks],
    )


@router.get("/modules/{module_slug}/lessons/{lesson_slug}/quiz")
def get_quiz(
    module_slug: str, lesson_slug: str, session: SessionDep
) -> list[QuestionOut]:
    """Return a lesson's quiz questions. Correct answers are never included."""
    lesson_id = session.scalar(
        select(Lesson.id)
        .join(Module, Lesson.module_id == Module.id)
        .where(Module.slug == module_slug, Lesson.slug == lesson_slug)
    )
    if lesson_id is None:
        raise HTTPException(status_code=404, detail="Lesson not found")

    questions = session.scalars(
        select(QuizQuestion)
        .where(QuizQuestion.lesson_id == lesson_id)
        .options(selectinload(QuizQuestion.options), selectinload(QuizQuestion.ayah))
        .order_by(QuizQuestion.id)
    )
    return [
        QuestionOut(
            id=question.id,
            question_type=question.question_type,
            prompt=question.prompt,
            ayah_text=question.ayah.text_uthmani if question.ayah else None,
            options=[OptionOut(id=o.id, text=o.text)
                     for o in question.options],
        )
        for question in questions
    ]


@router.post("/questions/{question_id}/check")
def check_answer(
    question_id: int, answer: AnswerIn, session: SessionDep
) -> AnswerResult:
    """Check one answer. Only now does the server reveal the correct option."""
    question = session.scalars(
        select(QuizQuestion)
        .where(QuizQuestion.id == question_id)
        .options(selectinload(QuizQuestion.options))
    ).one_or_none()
    if question is None:
        raise HTTPException(status_code=404, detail="Question not found")

    if answer.option_id not in {option.id for option in question.options}:
        raise HTTPException(
            status_code=400, detail="That option does not belong to this question"
        )

    correct = next(option for option in question.options if option.is_correct)
    return AnswerResult(
        correct=answer.option_id == correct.id,
        correct_option_id=correct.id,
        explanation=question.explanation,
    )
