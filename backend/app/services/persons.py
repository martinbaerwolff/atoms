import uuid
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.models.person import Person
from app.schemas.person import PersonCreate, PersonUpdate


def list_persons(db: Session) -> list[Person]:
    return db.query(Person).filter(Person.deleted_at.is_(None)).all()


def get_person(db: Session, person_id: uuid.UUID) -> Person | None:
    return (
        db.query(Person)
        .filter(Person.id == person_id, Person.deleted_at.is_(None))
        .first()
    )


def create_person(db: Session, data: PersonCreate) -> Person:
    person = Person(**data.model_dump())
    db.add(person)
    db.commit()
    db.refresh(person)
    return person


def update_person(db: Session, person: Person, data: PersonUpdate) -> Person:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(person, field, value)
    db.commit()
    db.refresh(person)
    return person


def delete_person(db: Session, person: Person) -> None:
    person.deleted_at = datetime.now(UTC)
    db.commit()
