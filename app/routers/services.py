from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.models.service import Service
from app.models.user import User
from app.schemas.service import ServiceCreate, ServiceUpdate, ServiceOut
from app.dependencies import get_current_admin

router = APIRouter(prefix="/api/services", tags=["services"])


@router.get("", response_model=List[ServiceOut])
def list_services(db: Session = Depends(get_db)):
    return db.query(Service).order_by(Service.name).all()


@router.get("/{service_id}", response_model=ServiceOut)
def get_service(service_id: int, db: Session = Depends(get_db)):
    s = db.query(Service).filter(Service.id == service_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")
    return s


@router.post("", response_model=ServiceOut)
def create_service(
    data: ServiceCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    s = Service(**data.model_dump())
    db.add(s)
    db.commit()
    db.refresh(s)
    return s


@router.put("/{service_id}", response_model=ServiceOut)
def update_service(
    service_id: int,
    data: ServiceUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    s = db.query(Service).filter(Service.id == service_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(s, key, value)
    db.commit()
    db.refresh(s)
    return s


@router.delete("/{service_id}")
def delete_service(
    service_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    s = db.query(Service).filter(Service.id == service_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")
    db.delete(s)
    db.commit()
    return {"detail": "Servicio eliminado"}
