from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.meeting import Meeting
from app.models.person import Person
from app.schemas.meeting import MeetingCreate, MeetingUpdate


async def create_meeting(session: AsyncSession, data: MeetingCreate) -> Meeting:
    payload = data.model_dump(exclude={"participant_ids"})
    meeting = Meeting(**payload)
    if data.participant_ids:
        result = await session.execute(select(Person).where(Person.id.in_(data.participant_ids)))
        meeting.participants = list(result.scalars().all())
    session.add(meeting)
    await session.commit()
    await session.refresh(meeting)
    return meeting


async def list_meetings(session: AsyncSession) -> list[Meeting]:
    result = await session.execute(
        select(Meeting)
        .options(selectinload(Meeting.participants))
        .where(Meeting.deleted_at.is_(None))
        .order_by(Meeting.created_at.desc())
    )
    return list(result.scalars().all())


async def get_meeting(session: AsyncSession, meeting_id: uuid.UUID) -> Meeting | None:
    result = await session.execute(
        select(Meeting)
        .options(selectinload(Meeting.participants))
        .where(Meeting.id == meeting_id, Meeting.deleted_at.is_(None))
    )
    return result.scalar_one_or_none()


async def update_meeting(session: AsyncSession, meeting: Meeting, data: MeetingUpdate) -> Meeting:
    payload = data.model_dump(exclude_unset=True, exclude={"participant_ids"})
    for field, value in payload.items():
        setattr(meeting, field, value)
    if data.participant_ids is not None:
        result = await session.execute(select(Person).where(Person.id.in_(data.participant_ids)))
        meeting.participants = list(result.scalars().all())
    await session.commit()
    await session.refresh(meeting)
    return meeting


async def delete_meeting(session: AsyncSession, meeting: Meeting) -> None:
    meeting.deleted_at = datetime.now(UTC)
    await session.commit()
