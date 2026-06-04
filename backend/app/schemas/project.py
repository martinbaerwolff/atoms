import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ProjectCreate(BaseModel):
    name: str
    color: str | None = None
    icon: str | None = None


class ProjectUpdate(BaseModel):
    name: str | None = None
    color: str | None = None
    icon: str | None = None


class ProjectRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    color: str | None
    icon: str | None
    created_at: datetime
    updated_at: datetime
