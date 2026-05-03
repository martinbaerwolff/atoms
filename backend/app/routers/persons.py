from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_session
from app.schemas.person import PersonCreate, PersonRead, PersonUpdate
from app.services import persons as svc

router = APIRouter(prefix="/persons", tags=["persons"])

SessionDep = Annotated[AsyncSession, Depends(get_session)]


@router.get("", response_model=list[PersonRead])
async def list_persons(session: SessionDep) -> list[PersonRead]:
    return await svc.list_persons(session)  # type: ignore[return-value]


@router.post("", response_model=PersonRead, status_code=status.HTTP_201_CREATED)
async def create_person(session: SessionDep, data: PersonCreate) -> PersonRead:
    return await svc.create_person(session, data)  # type: ignore[return-value]


@router.get("/{person_id}", response_model=PersonRead)
async def get_person(session: SessionDep, person_id: uuid.UUID) -> PersonRead:
    person = await svc.get_person(session, person_id)
    if person is None:
        raise HTTPException(status_code=404, detail="Person not found")
    return person  # type: ignore[return-value]


@router.patch("/{person_id}", response_model=PersonRead)
async def update_person(
    session: SessionDep, person_id: uuid.UUID, data: PersonUpdate
) -> PersonRead:
    person = await svc.get_person(session, person_id)
    if person is None:
        raise HTTPException(status_code=404, detail="Person not found")
    return await svc.update_person(session, person, data)  # type: ignore[return-value]


@router.delete("/{person_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_person(session: SessionDep, person_id: uuid.UUID) -> None:
    person = await svc.get_person(session, person_id)
    if person is None:
        raise HTTPException(status_code=404, detail="Person not found")
    await svc.delete_person(session, person)
