from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Index, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.atom import Atom
    from app.models.meeting import Meeting


class Person(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "persons"

    slug: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    email: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    atoms: Mapped[list[Atom]] = relationship(
        secondary="atom_persons", back_populates="persons", lazy="select"
    )
    meetings: Mapped[list[Meeting]] = relationship(
        secondary="meeting_participants", back_populates="participants", lazy="select"
    )

    __table_args__ = (
        Index("ix_persons_created_at", "created_at"),
        Index("ix_persons_deleted_at", "deleted_at"),
    )
