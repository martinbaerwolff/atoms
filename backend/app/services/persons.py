from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.person import Person
from app.schemas.person import PersonCreate, PersonUpdate


async def create_person(session: AsyncSession, data: PersonCreate) -> Person:
    person = Person(**data.model_dump())
    session.add(person)
    await session.commit()
    await session.refresh(person)
    return person


async def list_persons(session: AsyncSession) -> list[Person]:
    result = await session.execute(
        select(Person).where(Person.deleted_at.is_(None)).order_by(Person.created_at.desc())
    )
    return list(result.scalars().all())


async def get_person(session: AsyncSession, person_id: uuid.UUID) -> Person | None:
    result = await session.execute(
        select(Person).where(Person.id == person_id, Person.deleted_at.is_(None))
    )
    return result.scalar_one_or_none()


async def update_person(session: AsyncSession, person: Person, data: PersonUpdate) -> Person:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(person, field, value)
    await session.commit()
    await session.refresh(person)
    return person


async def delete_person(session: AsyncSession, person: Person) -> None:
    person.deleted_at = datetime.now(UTC)
    await session.commit()
