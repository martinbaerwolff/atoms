from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_session
from app.schemas.atom import AtomRead
from app.services import atoms as atom_svc

router = APIRouter(prefix="/views", tags=["views"])

SessionDep = Annotated[AsyncSession, Depends(get_session)]


@router.get("/inbox", response_model=list[AtomRead])
async def inbox(session: SessionDep) -> list[AtomRead]:
    return await atom_svc.view_inbox(session)  # type: ignore[return-value]
