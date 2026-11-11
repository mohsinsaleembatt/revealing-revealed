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
    notice: Mapped[str] = mapped_column(Text)
    file_sha256: Mapped[str] = mapped_column(String(64))
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
