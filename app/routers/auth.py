from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext
import logging

from app.db.database import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, Token, UserOut
from app.dependencies import create_access_token, get_current_user

router = APIRouter(prefix="/api/auth", tags=["auth"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
logger = logging.getLogger(__name__)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)


@router.post("/login", response_model=Token)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    # Buscar usuario
    user = db.query(User).filter(User.email == data.email).first()

    if not user:
        logger.warning(f"Login fallido: email no encontrado [{data.email}]")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
        )

    if not verify_password(data.password, user.hashed_password):
        logger.warning(f"Login fallido: contraseña incorrecta para [{data.email}]")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
        )

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Usuario desactivado")

    token = create_access_token({"sub": str(user.id), "email": user.email})
    logger.info(f"Login exitoso: {data.email}")
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/check-admin")
def check_admin(db: Session = Depends(get_db)):
    """Endpoint de diagnóstico: verifica si el admin existe en la DB."""
    from app.core.config import ADMIN_EMAIL
    user = db.query(User).filter(User.email == ADMIN_EMAIL).first()
    if not user:
        return {"exists": False, "email": ADMIN_EMAIL, "message": "Admin no encontrado. Ejecuta: python -m app.seed"}
    return {
        "exists": True,
        "email": user.email,
        "name": user.name,
        "is_active": user.is_active,
        "is_admin": user.is_admin,
        "has_password_hash": bool(user.hashed_password),
    }
