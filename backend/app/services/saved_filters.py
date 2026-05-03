from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.saved_filter import SavedFilter
from app.schemas.saved_filter import SavedFilterCreate, SavedFilterUpdate


async def create_saved_filter(session: AsyncSession, data: SavedFilterCreate) -> SavedFilter:
    sf = SavedFilter(**data.model_dump())
    session.add(sf)
    await session.commit()
    await session.refresh(sf)
    return sf


async def list_saved_filters(session: AsyncSession) -> list[SavedFilter]:
    result = await session.execute(
        select(SavedFilter)
        .where(SavedFilter.deleted_at.is_(None))
        .order_by(SavedFilter.created_at.desc())
    )
    return list(result.scalars().all())


async def get_saved_filter(session: AsyncSession, filter_id: uuid.UUID) -> SavedFilter | None:
    result = await session.execute(
        select(SavedFilter).where(SavedFilter.id == filter_id, SavedFilter.deleted_at.is_(None))
    )
    return result.scalar_one_or_none()


async def update_saved_filter(
    session: AsyncSession, sf: SavedFilter, data: SavedFilterUpdate
) -> SavedFilter:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(sf, field, value)
    await session.commit()
    await session.refresh(sf)
    return sf


async def delete_saved_filter(session: AsyncSession, sf: SavedFilter) -> None:
    sf.deleted_at = datetime.now(UTC)
    await session.commit()
