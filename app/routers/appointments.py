from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta

from app.db.database import get_db
from app.models.appointment import Appointment, AppointmentStatus
from app.models.professional import Professional
from app.models.service import Service
from app.models.client import Client
from app.models.user import User
from app.schemas.appointment import (
    AppointmentCreate, AppointmentUpdate, AppointmentOut, AvailabilityRequest
)
from app.dependencies import get_current_admin
from app.email_utils import send_appointment_confirmation

router = APIRouter(prefix="/api/appointments", tags=["appointments"])


def _calculate_end(start: datetime, duration_minutes: int) -> datetime:
    return start + timedelta(minutes=duration_minutes)


def _check_conflict(db: Session, professional_id: int, start: datetime,
                    end: datetime, exclude_id: int = None) -> bool:
    """Retorna True si hay conflicto de horario."""
    q = db.query(Appointment).filter(
        Appointment.professional_id == professional_id,
        Appointment.status.notin_([AppointmentStatus.cancelled]),
        Appointment.start_datetime < end,
        Appointment.end_datetime > start,
    )
    if exclude_id:
        q = q.filter(Appointment.id != exclude_id)
    return q.first() is not None


@router.get("/availability")
def get_availability(
    professional_id: int = Query(...),
    service_id: int = Query(...),
    date: str = Query(..., description="YYYY-MM-DD"),
    db: Session = Depends(get_db),
):
    """Retorna los slots disponibles para un profesional/servicio/día."""
    prof = db.query(Professional).filter(Professional.id == professional_id).first()
    if not prof:
        raise HTTPException(status_code=404, detail="Profesional no encontrado")

    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")

    try:
        day = datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de fecha inválido. Usa YYYY-MM-DD")

    # Verificar día laboral
    weekday = day.weekday()  # 0=lunes
    working_days = [int(d) for d in prof.working_days.split(",") if d.strip()]
    if weekday not in working_days:
        return {"date": date, "slots": [], "reason": "Profesional no trabaja este día"}

    # Construir slots
    work_start = datetime.strptime(prof.work_start, "%H:%M")
    work_end = datetime.strptime(prof.work_end, "%H:%M")
    duration = service.duration_minutes
    slot_step = 30  # cada 30 minutos

    current = day.replace(hour=work_start.hour, minute=work_start.minute, second=0, microsecond=0)
    end_of_day = day.replace(hour=work_end.hour, minute=work_end.minute, second=0, microsecond=0)

    slots = []
    now = datetime.now()

    while current + timedelta(minutes=duration) <= end_of_day:
        slot_end = current + timedelta(minutes=duration)
        if current > now:  # no ofrecer slots pasados
            conflict = _check_conflict(db, professional_id, current, slot_end)
            slots.append({
                "start": current.isoformat(),
                "end": slot_end.isoformat(),
                "available": not conflict,
            })
        current += timedelta(minutes=slot_step)

    return {"date": date, "slots": slots}


@router.get("", response_model=List[AppointmentOut])
def list_appointments(
    status: str = Query(None),
    date: str = Query(None, description="YYYY-MM-DD"),
    professional_id: int = Query(None),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    q = db.query(Appointment)
    if status:
        q = q.filter(Appointment.status == status)
    if professional_id:
        q = q.filter(Appointment.professional_id == professional_id)
    if date:
        try:
            day = datetime.strptime(date, "%Y-%m-%d")
            q = q.filter(
                Appointment.start_datetime >= day,
                Appointment.start_datetime < day + timedelta(days=1),
            )
        except ValueError:
            pass
    return q.order_by(Appointment.start_datetime.desc()).all()


@router.get("/{appt_id}", response_model=AppointmentOut)
def get_appointment(
    appt_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    a = db.query(Appointment).filter(Appointment.id == appt_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    return a


@router.post("", response_model=AppointmentOut)
def create_appointment(
    data: AppointmentCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    service = db.query(Service).filter(Service.id == data.service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")

    client = db.query(Client).filter(Client.id == data.client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    prof = db.query(Professional).filter(Professional.id == data.professional_id).first()
    if not prof:
        raise HTTPException(status_code=404, detail="Profesional no encontrado")

    end_dt = _calculate_end(data.start_datetime, service.duration_minutes)

    if _check_conflict(db, data.professional_id, data.start_datetime, end_dt):
        raise HTTPException(status_code=409, detail="Conflicto de horario: el profesional ya tiene una reserva en ese horario")

    appt = Appointment(
        client_id=data.client_id,
        professional_id=data.professional_id,
        service_id=data.service_id,
        start_datetime=data.start_datetime,
        end_datetime=end_dt,
        status=AppointmentStatus.confirmed,
        notes=data.notes,
        price_charged=service.price,
    )
    db.add(appt)
    db.commit()
    db.refresh(appt)

    if client.email:
        send_appointment_confirmation(
            client.email, client.name,
            service.name, prof.name, data.start_datetime
        )

    return appt


@router.put("/{appt_id}", response_model=AppointmentOut)
def update_appointment(
    appt_id: int,
    data: AppointmentUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    a = db.query(Appointment).filter(Appointment.id == appt_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(a, key, value)
    db.commit()
    db.refresh(a)
    return a


@router.delete("/{appt_id}")
def delete_appointment(
    appt_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    a = db.query(Appointment).filter(Appointment.id == appt_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    db.delete(a)
    db.commit()
    return {"detail": "Reserva eliminada"}
