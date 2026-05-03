from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_session
from app.schemas.project import ProjectCreate, ProjectRead, ProjectUpdate
from app.services import projects as svc

router = APIRouter(prefix="/projects", tags=["projects"])

SessionDep = Annotated[AsyncSession, Depends(get_session)]


@router.get("", response_model=list[ProjectRead])
async def list_projects(session: SessionDep) -> list[ProjectRead]:
    return await svc.list_projects(session)  # type: ignore[return-value]


@router.post("", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
async def create_project(session: SessionDep, data: ProjectCreate) -> ProjectRead:
    return await svc.create_project(session, data)  # type: ignore[return-value]


@router.get("/{project_id}", response_model=ProjectRead)
async def get_project(session: SessionDep, project_id: uuid.UUID) -> ProjectRead:
    project = await svc.get_project(session, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project  # type: ignore[return-value]


@router.patch("/{project_id}", response_model=ProjectRead)
async def update_project(
    session: SessionDep, project_id: uuid.UUID, data: ProjectUpdate
) -> ProjectRead:
    project = await svc.get_project(session, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return await svc.update_project(session, project, data)  # type: ignore[return-value]


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(session: SessionDep, project_id: uuid.UUID) -> None:
    project = await svc.get_project(session, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    await svc.delete_project(session, project)
