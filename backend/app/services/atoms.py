from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.atom import Atom
from app.models.person import Person
from app.schemas.atom import AtomCreate, AtomUpdate


def _base_query() -> Select[tuple[Atom]]:
    return select(Atom).options(selectinload(Atom.persons)).where(Atom.deleted_at.is_(None))


async def create_atom(session: AsyncSession, data: AtomCreate) -> Atom:
    payload = data.model_dump(exclude={"person_ids"})
    atom = Atom(**payload)
    if data.person_ids:
        result = await session.execute(select(Person).where(Person.id.in_(data.person_ids)))
        atom.persons = list(result.scalars().all())
    session.add(atom)
    await session.commit()
    await session.refresh(atom)
    return atom


async def list_atoms(session: AsyncSession, q: str | None = None) -> list[Atom]:
    stmt = _base_query()
    if q:
        stmt = stmt.where(
            func.to_tsvector("german", Atom.content).op("@@")(func.plainto_tsquery("german", q))
        )
    result = await session.execute(stmt.order_by(Atom.created_at.desc()))
    return list(result.scalars().all())


async def get_atom(session: AsyncSession, atom_id: uuid.UUID) -> Atom | None:
    result = await session.execute(_base_query().where(Atom.id == atom_id))
    return result.scalar_one_or_none()


async def update_atom(session: AsyncSession, atom: Atom, data: AtomUpdate) -> Atom:
    payload = data.model_dump(exclude_unset=True, exclude={"person_ids"})
    for field, value in payload.items():
        setattr(atom, field, value)
    if data.person_ids is not None:
        result = await session.execute(select(Person).where(Person.id.in_(data.person_ids)))
        atom.persons = list(result.scalars().all())
    await session.commit()
    await session.refresh(atom)
    return atom


async def delete_atom(session: AsyncSession, atom: Atom) -> None:
    atom.deleted_at = datetime.now(UTC)
    await session.commit()


async def view_inbox(session: AsyncSession) -> list[Atom]:
    result = await session.execute(
        _base_query().where(Atom.inbox.is_(True)).order_by(Atom.created_at.desc())
    )
    return list(result.scalars().all())
