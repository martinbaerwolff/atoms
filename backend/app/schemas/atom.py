from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict

AtomType = Literal["note", "task", "event", "reminder", "reference"]
AtomStatus = Literal["open", "in_progress", "done", "cancelled", "waiting"]
AtomPriority = Literal["low", "medium", "high", "urgent"]


class AtomCreate(BaseModel):
    slug: str
    content: str = ""
    content_json: dict[str, Any] | None = None
    type: AtomType = "note"
    status: AtomStatus = "open"
    priority: AtomPriority = "medium"
    inbox: bool = True
    reminder: datetime | None = None
    deadline: datetime | None = None
    deadline_hard: bool = False
    project_id: uuid.UUID | None = None
    meeting_id: uuid.UUID | None = None
    assigned_to: uuid.UUID | None = None
    person_ids: list[uuid.UUID] = []


class AtomUpdate(BaseModel):
    content: str | None = None
    content_json: dict[str, Any] | None = None
    type: AtomType | None = None
    status: AtomStatus | None = None
    priority: AtomPriority | None = None
    inbox: bool | None = None
    reminder: datetime | None = None
    deadline: datetime | None = None
    deadline_hard: bool | None = None
    project_id: uuid.UUID | None = None
    meeting_id: uuid.UUID | None = None
    assigned_to: uuid.UUID | None = None
    person_ids: list[uuid.UUID] | None = None


class AtomRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    slug: str
    content: str
    content_json: dict[str, Any] | None
    type: str
    status: str
    priority: str
    inbox: bool
    reminder: datetime | None
    deadline: datetime | None
    deadline_hard: bool
    project_id: uuid.UUID | None
    meeting_id: uuid.UUID | None
    assigned_to: uuid.UUID | None
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None
