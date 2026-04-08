from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.appointment import AppointmentStatus
from app.schemas.client import ClientOut
from app.schemas.service import ServiceOut
from app.schemas.professional import ProfessionalOut


class AppointmentCreate(BaseModel):
    client_id: int
    professional_id: int
    service_id: int
    start_datetime: datetime
    notes: Optional[str] = None


class AppointmentPublicCreate(BaseModel):
    """Para el formulario público sin login."""
    client_name: str
    client_email: Optional[str] = None
    client_phone: Optional[str] = None
    professional_id: int
    service_id: int
    start_datetime: datetime
    notes: Optional[str] = None


class AppointmentUpdate(BaseModel):
    status: Optional[AppointmentStatus] = None
    notes: Optional[str] = None
    price_charged: Optional[float] = None


class AppointmentOut(BaseModel):
    id: int
    client_id: int
    professional_id: int
    service_id: int
    start_datetime: datetime
    end_datetime: datetime
    status: AppointmentStatus
    notes: Optional[str] = None
    price_charged: Optional[float] = None
    created_at: Optional[datetime] = None
    client: Optional[ClientOut] = None
    professional: Optional[ProfessionalOut] = None
    service: Optional[ServiceOut] = None

    class Config:
        from_attributes = True


class AvailabilityRequest(BaseModel):
    professional_id: int
    service_id: int
    date: str  # "YYYY-MM-DD"
