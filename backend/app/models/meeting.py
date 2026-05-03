from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, ForeignKey, Index, Table, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.atom import Atom
    from app.models.person import Person
    from app.models.project import Project


meeting_participants = Table(
    "meeting_participants",
    Base.metadata,
    Column("meeting_id", Uuid, ForeignKey("meetings.id", ondelete="CASCADE"), primary_key=True),
    Column("person_id", Uuid, ForeignKey("persons.id", ondelete="CASCADE"), primary_key=True),
)


class Meeting(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "meetings"

    slug: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    date: Mapped[str | None] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    project_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("projects.id", ondelete="SET NULL"), nullable=True
    )
    project: Mapped[Project | None] = relationship(back_populates="meetings", lazy="select")
    participants: Mapped[list[Person]] = relationship(
        secondary="meeting_participants", back_populates="meetings", lazy="select"
    )
    atoms: Mapped[list[Atom]] = relationship(back_populates="meeting", lazy="select")

    __table_args__ = (
        Index("ix_meetings_date", "date"),
        Index("ix_meetings_project_id", "project_id"),
        Index("ix_meetings_created_at", "created_at"),
        Index("ix_meetings_deleted_at", "deleted_at"),
    )
