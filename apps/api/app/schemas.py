"""Shapes of the data the API sends out."""

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    field_validator,
    model_validator,
)

from app.validation import validate_display_name, validate_password


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


class JuzSummary(BaseModel):
    number: int
    start_reference: str  # e.g. "1:1"
    end_reference: str  # e.g. "2:141"
    ayah_count: int


class JuzSurahOut(BaseModel):
    number: int
    name_arabic: str
    name_transliteration: str
    name_english: str
    first_ayah_number: int
    last_ayah_number: int
    verses_in_juz: int
    total_verses: int
    is_complete: bool  # whether the whole surah falls inside this juz


class JuzDetail(JuzSummary):
    surahs: list[JuzSurahOut]


class PageSurah(BaseModel):
    number: int
    name_arabic: str
    name_transliteration: str
    name_english: str


class PageVerse(BaseModel):
    surah_number: int
    number: int
    text_uthmani: str  # exactly as stored from the verified source


class PageDetail(BaseModel):
    number: int
    juz_number: int | None
    surahs: list[PageSurah]
    verses: list[PageVerse]


class MessageOut(BaseModel):
    message: str


class SignUpIn(BaseModel):
    display_name: str
    email: EmailStr
    password: str
    accepted_terms: bool

    @field_validator("display_name")
    @classmethod
    def check_display_name(cls, value: str) -> str:
        return validate_display_name(value)

    @field_validator("email")
    @classmethod
    def lower_case_email(cls, value: str) -> str:
        # One spelling per address, so Test@x.com and test@x.com are the same account.
        return value.lower()

    @field_validator("password")
    @classmethod
    def check_password(cls, value: str) -> str:
        return validate_password(value)

    @field_validator("accepted_terms")
    @classmethod
    def check_terms(cls, value: bool) -> bool:
        if not value:
            raise ValueError("You must accept the terms to create an account.")
        return value

    @model_validator(mode="after")
    def password_must_not_contain_personal_details(self) -> "SignUpIn":
        password = self.password.lower()
        local_part = self.email.split("@")[0]
        if (
            password == self.display_name.lower()
            or password == self.email
            or (len(local_part) >= 6 and local_part in password)
        ):
            raise ValueError(
                "Do not use your name or email address in your password.")
        return self
