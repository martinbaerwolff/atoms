import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PersonCreate(BaseModel):
    name: str
    photo_url: str | None = None
    organizations: list[str] = []


class PersonUpdate(BaseModel):
    name: str | None = None
    photo_url: str | None = None
    organizations: list[str] | None = None


class PersonRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    photo_url: str | None
    organizations: list[str]
    created_at: datetime
    updated_at: datetime
