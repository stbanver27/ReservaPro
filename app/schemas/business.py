from pydantic import BaseModel
from typing import Optional


class BusinessBase(BaseModel):
    name: str
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    description: Optional[str] = None
    open_time: Optional[str] = "09:00"
    close_time: Optional[str] = "19:00"
    slot_duration: Optional[int] = 30
    logo_url: Optional[str] = None


class BusinessCreate(BusinessBase):
    pass


class BusinessUpdate(BusinessBase):
    name: Optional[str] = None


class BusinessOut(BusinessBase):
    id: int

    class Config:
        from_attributes = True
