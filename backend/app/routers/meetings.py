from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_session
from app.schemas.meeting import MeetingCreate, MeetingRead, MeetingUpdate
from app.services import meetings as svc

router = APIRouter(prefix="/meetings", tags=["meetings"])

SessionDep = Annotated[AsyncSession, Depends(get_session)]


@router.get("", response_model=list[MeetingRead])
async def list_meetings(session: SessionDep) -> list[MeetingRead]:
    return await svc.list_meetings(session)  # type: ignore[return-value]


@router.post("", response_model=MeetingRead, status_code=status.HTTP_201_CREATED)
async def create_meeting(session: SessionDep, data: MeetingCreate) -> MeetingRead:
    return await svc.create_meeting(session, data)  # type: ignore[return-value]


@router.get("/{meeting_id}", response_model=MeetingRead)
async def get_meeting(session: SessionDep, meeting_id: uuid.UUID) -> MeetingRead:
    meeting = await svc.get_meeting(session, meeting_id)
    if meeting is None:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return meeting  # type: ignore[return-value]


@router.patch("/{meeting_id}", response_model=MeetingRead)
async def update_meeting(
    session: SessionDep, meeting_id: uuid.UUID, data: MeetingUpdate
) -> MeetingRead:
    meeting = await svc.get_meeting(session, meeting_id)
    if meeting is None:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return await svc.update_meeting(session, meeting, data)  # type: ignore[return-value]


@router.delete("/{meeting_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_meeting(session: SessionDep, meeting_id: uuid.UUID) -> None:
    meeting = await svc.get_meeting(session, meeting_id)
    if meeting is None:
        raise HTTPException(status_code=404, detail="Meeting not found")
    await svc.delete_meeting(session, meeting)
