import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import app.services.atoms as svc
from app.deps import get_db
from app.schemas.atom import AtomCreate, AtomRead, AtomUpdate

router = APIRouter(prefix="/atoms", tags=["atoms"])


@router.get("/", response_model=list[AtomRead])
def list_atoms(
    type: str | None = None,
    filter_badge: str | None = None,
    db: Session = Depends(get_db),
):
    return svc.list_atoms(db, type=type, filter_badge=filter_badge)


@router.post("/", response_model=AtomRead, status_code=status.HTTP_201_CREATED)
def create_atom(data: AtomCreate, db: Session = Depends(get_db)):
    return svc.create_atom(db, data)


@router.get("/{atom_id}", response_model=AtomRead)
def get_atom(atom_id: uuid.UUID, db: Session = Depends(get_db)):
    atom = svc.get_atom(db, atom_id)
    if not atom:
        raise HTTPException(status_code=404, detail="Atom not found")
    return atom


@router.patch("/{atom_id}", response_model=AtomRead)
def update_atom(atom_id: uuid.UUID, data: AtomUpdate, db: Session = Depends(get_db)):
    atom = svc.get_atom(db, atom_id)
    if not atom:
        raise HTTPException(status_code=404, detail="Atom not found")
    return svc.update_atom(db, atom, data)


@router.delete("/{atom_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_atom(atom_id: uuid.UUID, db: Session = Depends(get_db)):
    atom = svc.get_atom(db, atom_id)
    if not atom:
        raise HTTPException(status_code=404, detail="Atom not found")
    svc.delete_atom(db, atom)
