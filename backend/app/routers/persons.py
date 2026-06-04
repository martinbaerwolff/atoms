import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import app.services.persons as svc
from app.deps import get_db
from app.schemas.person import PersonCreate, PersonRead, PersonUpdate

router = APIRouter(prefix="/persons", tags=["persons"])


@router.get("/", response_model=list[PersonRead])
def list_persons(db: Session = Depends(get_db)):
    return svc.list_persons(db)


@router.post("/", response_model=PersonRead, status_code=status.HTTP_201_CREATED)
def create_person(data: PersonCreate, db: Session = Depends(get_db)):
    return svc.create_person(db, data)


@router.get("/{person_id}", response_model=PersonRead)
def get_person(person_id: uuid.UUID, db: Session = Depends(get_db)):
    person = svc.get_person(db, person_id)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    return person


@router.patch("/{person_id}", response_model=PersonRead)
def update_person(person_id: uuid.UUID, data: PersonUpdate, db: Session = Depends(get_db)):
    person = svc.get_person(db, person_id)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    return svc.update_person(db, person, data)


@router.delete("/{person_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_person(person_id: uuid.UUID, db: Session = Depends(get_db)):
    person = svc.get_person(db, person_id)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    svc.delete_person(db, person)
