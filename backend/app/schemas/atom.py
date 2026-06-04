import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict

from app.schemas.person import PersonRead
from app.schemas.project import ProjectRead

AtomType = Literal["note", "thought", "task", "decision"]
AtomStatus = Literal["open", "in_progress", "blocked", "done", "cancelled"]
AtomPriority = Literal["high", "medium", "low"]
AtomComplexity = Literal["deep", "shallow", "routine"]


class AtomCreate(BaseModel):
    title: str
    content: str = ""
    type: AtomType
    captured: bool = False
    status: AtomStatus | None = None
    priority: AtomPriority | None = None
    complexity: AtomComplexity | None = None
    deadline_date: datetime | None = None
    alarm_date: datetime | None = None
    source_url: str | None = None
    responsible_ids: list[uuid.UUID] = []
    participant_ids: list[uuid.UUID] = []
    project_ids: list[uuid.UUID] = []


class AtomUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    type: AtomType | None = None
    captured: bool | None = None
    status: AtomStatus | None = None
    priority: AtomPriority | None = None
    complexity: AtomComplexity | None = None
    deadline_date: datetime | None = None
    alarm_date: datetime | None = None
    source_url: str | None = None
    responsible_ids: list[uuid.UUID] | None = None
    participant_ids: list[uuid.UUID] | None = None
    project_ids: list[uuid.UUID] | None = None


class AtomRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    content: str
    type: str
    captured: bool
    status: str | None
    priority: str | None
    complexity: str | None
    deadline_date: datetime | None
    alarm_date: datetime | None
    source_url: str | None
    responsible: list[PersonRead]
    participants: list[PersonRead]
    projects: list[ProjectRead]
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None
