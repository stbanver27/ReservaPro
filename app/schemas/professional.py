from pydantic import BaseModel
from typing import Optional


class ProfessionalBase(BaseModel):
    name: str
    specialty: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None
    is_active: bool = True
    working_days: Optional[str] = "0,1,2,3,4"
    work_start: Optional[str] = "09:00"
    work_end: Optional[str] = "18:00"


class ProfessionalCreate(ProfessionalBase):
    pass


class ProfessionalUpdate(BaseModel):
    name: Optional[str] = None
    specialty: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None
    is_active: Optional[bool] = None
    working_days: Optional[str] = None
    work_start: Optional[str] = None
    work_end: Optional[str] = None


class ProfessionalOut(ProfessionalBase):
    id: int

    class Config:
        from_attributes = True
