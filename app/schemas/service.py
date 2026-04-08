from pydantic import BaseModel
from typing import Optional


class ServiceBase(BaseModel):
    name: str
    description: Optional[str] = None
    duration_minutes: int = 30
    price: float = 0.0
    is_active: bool = True


class ServiceCreate(ServiceBase):
    pass


class ServiceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    duration_minutes: Optional[int] = None
    price: Optional[float] = None
    is_active: Optional[bool] = None


class ServiceOut(ServiceBase):
    id: int

    class Config:
        from_attributes = True
