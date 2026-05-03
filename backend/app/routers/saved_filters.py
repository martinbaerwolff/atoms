from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_session
from app.schemas.saved_filter import SavedFilterCreate, SavedFilterRead, SavedFilterUpdate
from app.services import saved_filters as svc

router = APIRouter(prefix="/saved-filters", tags=["saved-filters"])

SessionDep = Annotated[AsyncSession, Depends(get_session)]


@router.get("", response_model=list[SavedFilterRead])
async def list_saved_filters(session: SessionDep) -> list[SavedFilterRead]:
    return await svc.list_saved_filters(session)  # type: ignore[return-value]


@router.post("", response_model=SavedFilterRead, status_code=status.HTTP_201_CREATED)
async def create_saved_filter(session: SessionDep, data: SavedFilterCreate) -> SavedFilterRead:
    return await svc.create_saved_filter(session, data)  # type: ignore[return-value]


@router.get("/{filter_id}", response_model=SavedFilterRead)
async def get_saved_filter(session: SessionDep, filter_id: uuid.UUID) -> SavedFilterRead:
    sf = await svc.get_saved_filter(session, filter_id)
    if sf is None:
        raise HTTPException(status_code=404, detail="Saved filter not found")
    return sf  # type: ignore[return-value]


@router.patch("/{filter_id}", response_model=SavedFilterRead)
async def update_saved_filter(
    session: SessionDep, filter_id: uuid.UUID, data: SavedFilterUpdate
) -> SavedFilterRead:
    sf = await svc.get_saved_filter(session, filter_id)
    if sf is None:
        raise HTTPException(status_code=404, detail="Saved filter not found")
    return await svc.update_saved_filter(session, sf, data)  # type: ignore[return-value]


@router.delete("/{filter_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_saved_filter(session: SessionDep, filter_id: uuid.UUID) -> None:
    sf = await svc.get_saved_filter(session, filter_id)
    if sf is None:
        raise HTTPException(status_code=404, detail="Saved filter not found")
    await svc.delete_saved_filter(session, sf)
