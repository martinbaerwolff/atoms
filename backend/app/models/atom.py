from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Index, Table, Text, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.meeting import Meeting
    from app.models.person import Person
    from app.models.project import Project


atom_persons = Table(
    "atom_persons",
    Base.metadata,
    Column("atom_id", Uuid, ForeignKey("atoms.id", ondelete="CASCADE"), primary_key=True),
    Column("person_id", Uuid, ForeignKey("persons.id", ondelete="CASCADE"), primary_key=True),
)


class Atom(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "atoms"

    slug: Mapped[str] = mapped_column(Text, unique=True, nullable=False)

    # Content
    content: Mapped[str] = mapped_column(Text, nullable=False, default="")
    content_json: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)

    # Classification
    type: Mapped[str] = mapped_column(Text, nullable=False, default="note")
    status: Mapped[str] = mapped_column(Text, nullable=False, default="open")
    priority: Mapped[str] = mapped_column(Text, nullable=False, default="medium")
    inbox: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Dates
    reminder: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    deadline: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    deadline_hard: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Relations
    project_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("projects.id", ondelete="SET NULL"), nullable=True
    )
    meeting_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("meetings.id", ondelete="SET NULL"), nullable=True
    )
    assigned_to: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("persons.id", ondelete="SET NULL"), nullable=True
    )

    project: Mapped[Project | None] = relationship(back_populates="atoms", lazy="select")
    meeting: Mapped[Meeting | None] = relationship(back_populates="atoms", lazy="select")
    assignee: Mapped[Person | None] = relationship(foreign_keys=[assigned_to], lazy="select")
    persons: Mapped[list[Person]] = relationship(
        secondary="atom_persons", back_populates="atoms", lazy="select"
    )

    __table_args__ = (
        Index("ix_atoms_type", "type"),
        Index("ix_atoms_status", "status"),
        Index("ix_atoms_inbox", "inbox"),
        Index("ix_atoms_project_id", "project_id"),
        Index("ix_atoms_meeting_id", "meeting_id"),
        Index("ix_atoms_assigned_to", "assigned_to"),
        Index("ix_atoms_deadline", "deadline"),
        Index("ix_atoms_reminder", "reminder"),
        Index("ix_atoms_created_at", "created_at"),
        Index("ix_atoms_deleted_at", "deleted_at"),
    )
