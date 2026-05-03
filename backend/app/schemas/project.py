from __future__ import annotations

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict

ProjectStatus = Literal["active", "on_hold", "completed", "cancelled"]


class ProjectCreate(BaseModel):
    slug: str
    name: str
    description: str | None = None
    status: ProjectStatus = "active"


class ProjectUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    status: ProjectStatus | None = None


class ProjectRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    slug: str
    name: str
    description: str | None
    status: str
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None
