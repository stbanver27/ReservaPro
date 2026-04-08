"""
Router público: formulario de reservas sin autenticación.
También sirve las vistas HTML via Jinja2.
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import timedelta

from app.db.database import get_db
from app.models.appointment import Appointment, AppointmentStatus
from app.models.professional import Professional
from app.models.service import Service
from app.models.client import Client
from app.schemas.appointment import AppointmentPublicCreate
from app.email_utils import send_appointment_confirmation

router = APIRouter(tags=["public"])
templates = Jinja2Templates(directory="templates")


def _calculate_end(start, duration_minutes):
    return start + timedelta(minutes=duration_minutes)


def _check_conflict(db, professional_id, start, end):
    return db.query(Appointment).filter(
        Appointment.professional_id == professional_id,
        Appointment.status.notin_([AppointmentStatus.cancelled]),
        Appointment.start_datetime < end,
        Appointment.end_datetime > start,
    ).first() is not None


# ─── HTML Views ──────────────────────────────────────────────────────────────

@router.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("public_booking.html", {"request": request})


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})


@router.get("/admin/services", response_class=HTMLResponse)
def services_page(request: Request):
    return templates.TemplateResponse("services.html", {"request": request})


@router.get("/admin/professionals", response_class=HTMLResponse)
def professionals_page(request: Request):
    return templates.TemplateResponse("professionals.html", {"request": request})


@router.get("/admin/clients", response_class=HTMLResponse)
def clients_page(request: Request):
    return templates.TemplateResponse("clients.html", {"request": request})


@router.get("/admin/appointments", response_class=HTMLResponse)
def appointments_page(request: Request):
    return templates.TemplateResponse("appointments.html", {"request": request})


@router.get("/admin/business", response_class=HTMLResponse)
def business_page(request: Request):
    return templates.TemplateResponse("business.html", {"request": request})


# ─── Public API ──────────────────────────────────────────────────────────────

@router.get("/api/public/services")
def public_services(db: Session = Depends(get_db)):
    return db.query(Service).filter(Service.is_active == True).order_by(Service.name).all()


@router.get("/api/public/professionals")
def public_professionals(db: Session = Depends(get_db)):
    return db.query(Professional).filter(Professional.is_active == True).order_by(Professional.name).all()


@router.post("/api/public/book")
def public_book(data: AppointmentPublicCreate, db: Session = Depends(get_db)):
    """Reserva pública sin login. Crea el cliente si no existe."""
    service = db.query(Service).filter(Service.id == data.service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")

    prof = db.query(Professional).filter(Professional.id == data.professional_id).first()
    if not prof:
        raise HTTPException(status_code=404, detail="Profesional no encontrado")

    # Buscar o crear cliente por email
    client = None
    if data.client_email:
        client = db.query(Client).filter(Client.email == data.client_email).first()

    if not client:
        client = Client(
            name=data.client_name,
            email=data.client_email,
            phone=data.client_phone,
        )
        db.add(client)
        db.flush()

    end_dt = _calculate_end(data.start_datetime, service.duration_minutes)

    if _check_conflict(db, data.professional_id, data.start_datetime, end_dt):
        raise HTTPException(
            status_code=409,
            detail="Ese horario ya no está disponible. Por favor elige otro."
        )

    appt = Appointment(
        client_id=client.id,
        professional_id=data.professional_id,
        service_id=data.service_id,
        start_datetime=data.start_datetime,
        end_datetime=end_dt,
        status=AppointmentStatus.pending,
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

    return {
        "detail": "Reserva registrada exitosamente. Te contactaremos para confirmar.",
        "appointment_id": appt.id,
        "status": appt.status,
    }
