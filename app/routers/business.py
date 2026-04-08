from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.business import Business
from app.models.user import User
from app.schemas.business import BusinessCreate, BusinessUpdate, BusinessOut
from app.dependencies import get_current_admin

router = APIRouter(prefix="/api/business", tags=["business"])


@router.get("", response_model=BusinessOut)
def get_business(db: Session = Depends(get_db)):
    biz = db.query(Business).first()
    if not biz:
        raise HTTPException(status_code=404, detail="Negocio no configurado")
    return biz


@router.post("", response_model=BusinessOut)
def create_business(
    data: BusinessCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    existing = db.query(Business).first()
    if existing:
        raise HTTPException(status_code=400, detail="Ya existe un negocio. Usa PUT para actualizar.")
    biz = Business(**data.model_dump())
    db.add(biz)
    db.commit()
    db.refresh(biz)
    return biz


@router.put("", response_model=BusinessOut)
def update_business(
    data: BusinessUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    biz = db.query(Business).first()
    if not biz:
        raise HTTPException(status_code=404, detail="Negocio no encontrado")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(biz, key, value)
    db.commit()
    db.refresh(biz)
    return biz
