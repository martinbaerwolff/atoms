from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PersonCreate(BaseModel):
    slug: str
    name: str
    email: str | None = None
    notes: str | None = None


class PersonUpdate(BaseModel):
    name: str | None = None
    email: str | None = None
    notes: str | None = None


class PersonRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    slug: str
    name: str
    email: str | None
    notes: str | None
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None
