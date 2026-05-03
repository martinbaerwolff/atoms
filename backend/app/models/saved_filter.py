from __future__ import annotations

from typing import Any

from sqlalchemy import Index, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class SavedFilter(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "saved_filters"

    slug: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    filter_json: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)

    __table_args__ = (
        Index("ix_saved_filters_created_at", "created_at"),
        Index("ix_saved_filters_deleted_at", "deleted_at"),
    )
