from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class SavedFilterCreate(BaseModel):
    slug: str
    name: str
    filter_json: dict[str, Any] = {}


class SavedFilterUpdate(BaseModel):
    name: str | None = None
    filter_json: dict[str, Any] | None = None


class SavedFilterRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    slug: str
    name: str
    filter_json: dict[str, Any]
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None
