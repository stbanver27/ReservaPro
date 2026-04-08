from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.models.professional import Professional
from app.models.user import User
from app.schemas.professional import ProfessionalCreate, ProfessionalUpdate, ProfessionalOut
from app.dependencies import get_current_admin

router = APIRouter(prefix="/api/professionals", tags=["professionals"])


@router.get("", response_model=List[ProfessionalOut])
def list_professionals(db: Session = Depends(get_db)):
    return db.query(Professional).order_by(Professional.name).all()


@router.get("/{prof_id}", response_model=ProfessionalOut)
def get_professional(prof_id: int, db: Session = Depends(get_db)):
    p = db.query(Professional).filter(Professional.id == prof_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Profesional no encontrado")
    return p


@router.post("", response_model=ProfessionalOut)
def create_professional(
    data: ProfessionalCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    p = Professional(**data.model_dump())
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


@router.put("/{prof_id}", response_model=ProfessionalOut)
def update_professional(
    prof_id: int,
    data: ProfessionalUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    p = db.query(Professional).filter(Professional.id == prof_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Profesional no encontrado")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(p, key, value)
    db.commit()
    db.refresh(p)
    return p


@router.delete("/{prof_id}")
def delete_professional(
    prof_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    p = db.query(Professional).filter(Professional.id == prof_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Profesional no encontrado")
    db.delete(p)
    db.commit()
    return {"detail": "Profesional eliminado"}
