from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_session
from app.schemas.atom import AtomCreate, AtomRead, AtomUpdate
from app.services import atoms as svc

router = APIRouter(prefix="/atoms", tags=["atoms"])

SessionDep = Annotated[AsyncSession, Depends(get_session)]


@router.get("", response_model=list[AtomRead])
async def list_atoms(
    session: SessionDep,
    q: Annotated[str | None, Query(description="Fulltext search")] = None,
) -> list[AtomRead]:
    return await svc.list_atoms(session, q=q)  # type: ignore[return-value]


@router.post("", response_model=AtomRead, status_code=status.HTTP_201_CREATED)
async def create_atom(session: SessionDep, data: AtomCreate) -> AtomRead:
    return await svc.create_atom(session, data)  # type: ignore[return-value]


@router.get("/{atom_id}", response_model=AtomRead)
async def get_atom(session: SessionDep, atom_id: uuid.UUID) -> AtomRead:
    atom = await svc.get_atom(session, atom_id)
    if atom is None:
        raise HTTPException(status_code=404, detail="Atom not found")
    return atom  # type: ignore[return-value]


@router.patch("/{atom_id}", response_model=AtomRead)
async def update_atom(session: SessionDep, atom_id: uuid.UUID, data: AtomUpdate) -> AtomRead:
    atom = await svc.get_atom(session, atom_id)
    if atom is None:
        raise HTTPException(status_code=404, detail="Atom not found")
    return await svc.update_atom(session, atom, data)  # type: ignore[return-value]


@router.delete("/{atom_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_atom(session: SessionDep, atom_id: uuid.UUID) -> None:
    atom = await svc.get_atom(session, atom_id)
    if atom is None:
        raise HTTPException(status_code=404, detail="Atom not found")
    await svc.delete_atom(session, atom)
