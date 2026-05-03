from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class MeetingCreate(BaseModel):
    slug: str
    title: str
    date: datetime | None = None
    notes: str | None = None
    project_id: uuid.UUID | None = None
    participant_ids: list[uuid.UUID] = []


class MeetingUpdate(BaseModel):
    title: str | None = None
    date: datetime | None = None
    notes: str | None = None
    project_id: uuid.UUID | None = None
    participant_ids: list[uuid.UUID] | None = None


class MeetingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    slug: str
    title: str
    date: datetime | None
    notes: str | None
    project_id: uuid.UUID | None
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None
