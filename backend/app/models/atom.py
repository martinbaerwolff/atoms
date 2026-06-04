from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Table, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.person import Person
    from app.models.project import Project

atom_responsible = Table(
    "atom_responsible",
    Base.metadata,
    Column("atom_id", UUID(as_uuid=True), ForeignKey("atoms.id", ondelete="CASCADE"), primary_key=True),
    Column("person_id", UUID(as_uuid=True), ForeignKey("persons.id", ondelete="CASCADE"), primary_key=True),
)

atom_participants = Table(
    "atom_participants",
    Base.metadata,
    Column("atom_id", UUID(as_uuid=True), ForeignKey("atoms.id", ondelete="CASCADE"), primary_key=True),
    Column("person_id", UUID(as_uuid=True), ForeignKey("persons.id", ondelete="CASCADE"), primary_key=True),
)

atom_projects = Table(
    "atom_projects",
    Base.metadata,
    Column("atom_id", UUID(as_uuid=True), ForeignKey("atoms.id", ondelete="CASCADE"), primary_key=True),
    Column("project_id", UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True),
)


class Atom(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "atoms"

    title: Mapped[str] = mapped_column(Text, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False, default="")
    type: Mapped[str] = mapped_column(Text, nullable=False)
    captured: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    status: Mapped[str | None] = mapped_column(Text, nullable=True)
    priority: Mapped[str | None] = mapped_column(Text, nullable=True)
    complexity: Mapped[str | None] = mapped_column(Text, nullable=True)
    deadline_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    alarm_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    source_url: Mapped[str | None] = mapped_column(Text, nullable=True)

    responsible: Mapped[list[Person]] = relationship(secondary=atom_responsible, lazy="select")
    participants: Mapped[list[Person]] = relationship(secondary=atom_participants, lazy="select")
    projects: Mapped[list[Project]] = relationship(secondary=atom_projects, lazy="select")
