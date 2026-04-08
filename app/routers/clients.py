from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.models.client import Client
from app.models.user import User
from app.schemas.client import ClientCreate, ClientUpdate, ClientOut
from app.dependencies import get_current_admin

router = APIRouter(prefix="/api/clients", tags=["clients"])


@router.get("", response_model=List[ClientOut])
def list_clients(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    return db.query(Client).order_by(Client.name).all()


@router.get("/{client_id}", response_model=ClientOut)
def get_client(
    client_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    c = db.query(Client).filter(Client.id == client_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return c


@router.post("", response_model=ClientOut)
def create_client(
    data: ClientCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    c = Client(**data.model_dump())
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


@router.put("/{client_id}", response_model=ClientOut)
def update_client(
    client_id: int,
    data: ClientUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    c = db.query(Client).filter(Client.id == client_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(c, key, value)
    db.commit()
    db.refresh(c)
    return c


@router.delete("/{client_id}")
def delete_client(
    client_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    c = db.query(Client).filter(Client.id == client_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    db.delete(c)
    db.commit()
    return {"detail": "Cliente eliminado"}
