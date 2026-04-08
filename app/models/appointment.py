import enum
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, ForeignKey, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base


class AppointmentStatus(str, enum.Enum):
    pending = "pending"
    confirmed = "confirmed"
    cancelled = "cancelled"
    completed = "completed"


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    professional_id = Column(Integer, ForeignKey("professionals.id"), nullable=False)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)

    start_datetime = Column(DateTime, nullable=False)
    end_datetime = Column(DateTime, nullable=False)

    status = Column(
        Enum(AppointmentStatus),
        default=AppointmentStatus.pending,
        nullable=False
    )
    notes = Column(Text)
    price_charged = Column(Float)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    client = relationship("Client", lazy="joined")
    professional = relationship("Professional", lazy="joined")
    service = relationship("Service", lazy="joined")
