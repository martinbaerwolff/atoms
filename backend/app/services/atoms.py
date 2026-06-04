import uuid
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.models.atom import Atom
from app.models.person import Person
from app.models.project import Project
from app.schemas.atom import AtomCreate, AtomUpdate


def _resolve_relations(db: Session, atom: Atom, responsible_ids, participant_ids, project_ids):
    if responsible_ids is not None:
        atom.responsible = db.query(Person).filter(Person.id.in_(responsible_ids)).all()
    if participant_ids is not None:
        atom.participants = db.query(Person).filter(Person.id.in_(participant_ids)).all()
    if project_ids is not None:
        atom.projects = db.query(Project).filter(Project.id.in_(project_ids)).all()


def list_atoms(
    db: Session,
    type: str | None = None,
    filter_badge: str | None = None,
) -> list[Atom]:
    now = datetime.now(UTC)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    query = db.query(Atom).filter(Atom.deleted_at.is_(None))

    if type:
        query = query.filter(Atom.type == type)

    if filter_badge == "inbox":
        query = query.filter(Atom.captured.is_(False))
    elif filter_badge == "created_today":
        query = query.filter(Atom.created_at >= today_start)
    elif filter_badge == "updated_today":
        query = query.filter(Atom.updated_at >= today_start)
    elif filter_badge == "overdue":
        query = query.filter(
            Atom.type == "task",
            Atom.deadline_date < now,
            Atom.status.notin_(["done", "cancelled"]),
        )

    return query.order_by(Atom.created_at.desc()).all()


def get_atom(db: Session, atom_id: uuid.UUID) -> Atom | None:
    return (
        db.query(Atom)
        .filter(Atom.id == atom_id, Atom.deleted_at.is_(None))
        .first()
    )


def create_atom(db: Session, data: AtomCreate) -> Atom:
    scalar_data = data.model_dump(exclude={"responsible_ids", "participant_ids", "project_ids"})
    atom = Atom(**scalar_data)
    _resolve_relations(db, atom, data.responsible_ids, data.participant_ids, data.project_ids)
    db.add(atom)
    db.commit()
    db.refresh(atom)
    return atom


def update_atom(db: Session, atom: Atom, data: AtomUpdate) -> Atom:
    update_data = data.model_dump(exclude_unset=True)
    responsible_ids = update_data.pop("responsible_ids", None)
    participant_ids = update_data.pop("participant_ids", None)
    project_ids = update_data.pop("project_ids", None)

    for field, value in update_data.items():
        setattr(atom, field, value)

    _resolve_relations(db, atom, responsible_ids, participant_ids, project_ids)
    db.commit()
    db.refresh(atom)
    return atom


def delete_atom(db: Session, atom: Atom) -> None:
    atom.deleted_at = datetime.now(UTC)
    db.commit()
