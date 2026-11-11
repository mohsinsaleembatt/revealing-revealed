"""Read-only endpoints that serve the Qur'anic text."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.database import get_session
from app.models import Source, Surah
from app.schemas import SourceOut, SurahDetail, SurahSummary

router = APIRouter(prefix="/quran", tags=["quran"])

# A short name for "a database session supplied by FastAPI".
SessionDep = Annotated[Session, Depends(get_session)]


@router.get("/surahs")
def list_surahs(session: SessionDep) -> list[SurahSummary]:
    """List all 114 surahs in order."""
    return list(session.scalars(select(Surah).order_by(Surah.number)))


@router.get("/surahs/{number}")
def get_surah(
    number: Annotated[int, Path(ge=1, le=114, description="Surah number, 1 to 114")],
    session: SessionDep,
) -> SurahDetail:
    """Return one surah with all of its verses."""
    surah = session.scalars(
        select(Surah)
        .where(Surah.number == number)
        .options(selectinload(Surah.ayahs))
    ).one_or_none()
    if surah is None:
        raise HTTPException(status_code=404, detail="Surah not found")
    return surah


@router.get("/sources")
def list_sources(session: SessionDep) -> list[SourceOut]:
    """List where the content comes from, with licences and required notices."""
    return list(session.scalars(select(Source).order_by(Source.id)))
