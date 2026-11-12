"""Database models: each class describes one table."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, UniqueConstraint, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Parent class of all models."""


class Source(Base):
    """Where content came from: its licence and the notice it requires."""

    __tablename__ = "source"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    url: Mapped[str] = mapped_column(String(500))
    licence: Mapped[str] = mapped_column(String(200))
    version: Mapped[str | None] = mapped_column(String(50))
    # The copyright notice, stored exactly as it appears in the source file.
    notice: Mapped[str | None] = mapped_column(Text)
    file_sha256: Mapped[str | None] = mapped_column(String(64))
    imported_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class Surah(Base):
    """A chapter of the Qur'an."""

    __tablename__ = "surah"

    id: Mapped[int] = mapped_column(primary_key=True)
    number: Mapped[int] = mapped_column(unique=True)  # 1 to 114
    name_arabic: Mapped[str] = mapped_column(String(50))
    name_transliteration: Mapped[str] = mapped_column(String(50))
    name_english: Mapped[str] = mapped_column(String(100))
    revelation_place: Mapped[str] = mapped_column(String(10))
    ayah_count: Mapped[int]
    source_id: Mapped[int] = mapped_column(ForeignKey("source.id"))

    ayahs: Mapped[list["Ayah"]] = relationship(
        back_populates="surah", order_by="Ayah.number"
    )


class Ayah(Base):
    """A verse of the Qur'an."""

    __tablename__ = "ayah"
    __table_args__ = (UniqueConstraint("surah_id", "number"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    surah_id: Mapped[int] = mapped_column(ForeignKey("surah.id"))
    number: Mapped[int]  # the verse number inside its surah
    # Stored exactly as in the verified source. Never edited by hand or code.
    text_uthmani: Mapped[str] = mapped_column(Text)
    source_id: Mapped[int] = mapped_column(ForeignKey("source.id"))

    surah: Mapped["Surah"] = relationship(back_populates="ayahs")


class Module(Base):
    """A group of lessons, such as 'Letters and Sounds'."""

    __tablename__ = "module"

    id: Mapped[int] = mapped_column(primary_key=True)
    number: Mapped[int] = mapped_column(unique=True)  # 0, 1, 2, ...
    slug: Mapped[str] = mapped_column(String(100), unique=True)
    title: Mapped[str] = mapped_column(String(200))
    summary: Mapped[str] = mapped_column(Text)

    lessons: Mapped[list["Lesson"]] = relationship(
        back_populates="module", order_by="Lesson.number"
    )


class Lesson(Base):
    """One lesson. Its text lives in a file under content/, not here."""

    __tablename__ = "lesson"
    __table_args__ = (
        UniqueConstraint("module_id", "number"),
        UniqueConstraint("module_id", "slug"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    module_id: Mapped[int] = mapped_column(ForeignKey("module.id"))
    number: Mapped[int]  # the order inside the module
    slug: Mapped[str] = mapped_column(String(100))
    title: Mapped[str] = mapped_column(String(200))
    goal: Mapped[str] = mapped_column(Text)
    # "draft", "reviewed" or "approved"
    review_status: Mapped[str] = mapped_column(String(20), default="draft")

    module: Mapped["Module"] = relationship(back_populates="lessons")
    blocks: Mapped[list["LessonBlock"]] = relationship(
        back_populates="lesson", order_by="LessonBlock.position"
    )


class LessonBlock(Base):
    """One piece of a lesson: either a paragraph of text or a Qur'anic verse."""

    __tablename__ = "lesson_block"
    __table_args__ = (UniqueConstraint("lesson_id", "position"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    lesson_id: Mapped[int] = mapped_column(ForeignKey("lesson.id"))
    position: Mapped[int]  # the order inside the lesson
    kind: Mapped[str] = mapped_column(String(20))  # "text" or "ayah"
    body: Mapped[str | None] = mapped_column(Text)  # for text blocks
    note: Mapped[str | None] = mapped_column(Text)
    # For verse blocks: the text is read from the ayah table, never copied.
    ayah_id: Mapped[int | None] = mapped_column(ForeignKey("ayah.id"))
    # For text blocks: where the claim comes from (the citation).
    source_id: Mapped[int | None] = mapped_column(ForeignKey("source.id"))
    source_location: Mapped[str | None] = mapped_column(String(200))

    lesson: Mapped["Lesson"] = relationship(back_populates="blocks")
    ayah: Mapped["Ayah | None"] = relationship()
    source: Mapped["Source | None"] = relationship()


class QuizQuestion(Base):
    """A multiple-choice question, generated from verified data."""

    __tablename__ = "quiz_question"

    id: Mapped[int] = mapped_column(primary_key=True)
    lesson_id: Mapped[int] = mapped_column(ForeignKey("lesson.id"))
    # The verse shown with the question, if it has one.
    ayah_id: Mapped[int | None] = mapped_column(ForeignKey("ayah.id"))
    question_type: Mapped[str] = mapped_column(String(30))
    prompt: Mapped[str] = mapped_column(Text)
    explanation: Mapped[str] = mapped_column(Text)
    # Generated questions still wait for review, like lessons do.
    review_status: Mapped[str] = mapped_column(String(20), default="draft")

    ayah: Mapped["Ayah | None"] = relationship()
    options: Mapped[list["QuizOption"]] = relationship(
        back_populates="question",
        cascade="all, delete-orphan",
        order_by="QuizOption.position",
    )


class QuizOption(Base):
    """One answer choice of a question."""

    __tablename__ = "quiz_option"
    __table_args__ = (UniqueConstraint("question_id", "position"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("quiz_question.id"))
    position: Mapped[int]
    text: Mapped[str] = mapped_column(String(200))
    is_correct: Mapped[bool]

    question: Mapped["QuizQuestion"] = relationship(back_populates="options")
