"""Read-only endpoints that serve the Qur'anic text."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.database import get_session
from app.models import Source, Surah
from app.schemas import SourceOut, SurahDetail, SurahSummary

from app.models import Ayah, Juz, MushafPage, Source, Surah
from app.schemas import (
    JuzDetail,
    JuzSummary,
    JuzSurahOut,
    PageDetail,
    PageSurah,
    PageVerse,
    SourceOut,
    SurahDetail,
    SurahSummary,
)

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


@router.get("/juz")
def list_juz(session: SessionDep) -> list[JuzSummary]:
    """List the 30 juz, each as a short summary."""
    rows = session.scalars(
        select(Juz)
        .options(
            selectinload(Juz.start_ayah).selectinload(Ayah.surah),
            selectinload(Juz.end_ayah).selectinload(Ayah.surah),
        )
        .order_by(Juz.number)
    )
    return [
        JuzSummary(
            number=row.number,
            start_reference=f"{row.start_ayah.surah.number}:{row.start_ayah.number}",
            end_reference=f"{row.end_ayah.surah.number}:{row.end_ayah.number}",
            ayah_count=row.end_ayah_id - row.start_ayah_id + 1,
        )
        for row in rows
    ]


@router.get("/juz/{number}")
def get_juz(
    number: Annotated[int, Path(ge=1, le=30, description="Juz number, 1 to 30")],
    session: SessionDep,
) -> JuzDetail:
    """Return one juz with the surahs (or parts of surahs) inside it."""
    juz = session.scalars(
        select(Juz)
        .where(Juz.number == number)
        .options(
            selectinload(Juz.start_ayah).selectinload(Ayah.surah),
            selectinload(Juz.end_ayah).selectinload(Ayah.surah),
        )
    ).one_or_none()
    if juz is None:
        raise HTTPException(status_code=404, detail="Juz not found")

    rows = session.execute(
        select(
            Surah.number,
            Surah.name_arabic,
            Surah.name_transliteration,
            Surah.name_english,
            Surah.ayah_count,
            func.min(Ayah.number).label("first_ayah_number"),
            func.max(Ayah.number).label("last_ayah_number"),
            func.count(Ayah.id).label("verses_in_juz"),
        )
        .join(Ayah, Ayah.surah_id == Surah.id)
        .where(Ayah.id.between(juz.start_ayah_id, juz.end_ayah_id))
        .group_by(Surah.id)
        .order_by(Surah.number)
    ).all()

    return JuzDetail(
        number=juz.number,
        start_reference=f"{juz.start_ayah.surah.number}:{juz.start_ayah.number}",
        end_reference=f"{juz.end_ayah.surah.number}:{juz.end_ayah.number}",
        ayah_count=juz.end_ayah_id - juz.start_ayah_id + 1,
        surahs=[
            JuzSurahOut(
                number=row.number,
                name_arabic=row.name_arabic,
                name_transliteration=row.name_transliteration,
                name_english=row.name_english,
                first_ayah_number=row.first_ayah_number,
                last_ayah_number=row.last_ayah_number,
                verses_in_juz=row.verses_in_juz,
                total_verses=row.ayah_count,
                is_complete=row.verses_in_juz == row.ayah_count,
            )
            for row in rows
        ],
    )


@router.get("/pages/{number}")
def get_page(
    number: Annotated[int, Path(ge=1, le=604, description="Page number, 1 to 604")],
    session: SessionDep,
) -> PageDetail:
    """Return the verses that belong on one Mushaf page."""
    page = session.scalars(
        select(MushafPage).where(MushafPage.number == number)
    ).one_or_none()
    if page is None:
        raise HTTPException(status_code=404, detail="Page not found")

    rows = session.execute(
        select(
            Surah.number.label("surah_number"),
            Surah.name_arabic,
            Surah.name_transliteration,
            Surah.name_english,
            Ayah.number.label("ayah_number"),
            Ayah.text_uthmani,
        )
        .join(Ayah, Ayah.surah_id == Surah.id)
        .where(Ayah.id.between(page.start_ayah_id, page.end_ayah_id))
        .order_by(Ayah.id)
    ).all()

    surahs: dict[int, PageSurah] = {}
    for row in rows:
        surahs.setdefault(
            row.surah_number,
            PageSurah(
                number=row.surah_number,
                name_arabic=row.name_arabic,
                name_transliteration=row.name_transliteration,
                name_english=row.name_english,
            ),
        )

    juz_number = session.scalar(
        select(Juz.number).where(
            Juz.start_ayah_id <= page.start_ayah_id,
            Juz.end_ayah_id >= page.start_ayah_id,
        )
    )

    return PageDetail(
        number=page.number,
        juz_number=juz_number,
        surahs=list(surahs.values()),
        verses=[
            PageVerse(
                surah_number=row.surah_number,
                number=row.ayah_number,
                text_uthmani=row.text_uthmani,
            )
            for row in rows
        ],
    )
