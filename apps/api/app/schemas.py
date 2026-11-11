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
    notice: str
