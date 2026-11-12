"""Shapes of the data the API sends out."""

from pydantic import BaseModel, ConfigDict


class OrmModel(BaseModel):
    """Base class: allows building these from database objects."""

    model_config = ConfigDict(from_attributes=True)


class SurahSummary(OrmModel):
    number: int
    name_arabic: str
    name_transliteration: str
    name_english: str
    revelation_place: str
    ayah_count: int


class AyahOut(OrmModel):
    number: int
    # Exactly as stored from the verified source; never modified.
    text_uthmani: str


class SurahDetail(SurahSummary):
    ayahs: list[AyahOut]


class SourceOut(OrmModel):
    name: str
    url: str
    licence: str
    version: str | None
    notice: str | None


class LessonSummary(OrmModel):
    number: int
    slug: str
    title: str
    goal: str
    review_status: str


class ModuleOut(OrmModel):
    number: int
    slug: str
    title: str
    summary: str
    lessons: list[LessonSummary]


class BlockOut(BaseModel):
    position: int
    kind: str  # "text" or "ayah"
    body: str | None = None
    note: str | None = None
    # For verse blocks: the reference and the text read from the verified table.
    ayah_reference: str | None = None
    ayah_text: str | None = None
    # For text blocks: the citation.
    source_name: str | None = None
    source_url: str | None = None
    source_location: str | None = None


class LessonDetail(BaseModel):
    module_slug: str
    module_title: str
    number: int
    slug: str
    title: str
    goal: str
    review_status: str
    blocks: list[BlockOut]


class OptionOut(BaseModel):
    id: int
    text: str  # note: the correct answer is deliberately not included


class QuestionOut(BaseModel):
    id: int
    question_type: str
    prompt: str
    ayah_text: str | None = None
    options: list[OptionOut]


class AnswerIn(BaseModel):
    option_id: int


class AnswerResult(BaseModel):
    correct: bool
    correct_option_id: int
    explanation: str
