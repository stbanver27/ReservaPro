from sqlalchemy import Column, Integer, String, Time, Text
from app.db.database import Base


class Business(Base):
    __tablename__ = "businesses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    address = Column(String(250))
    phone = Column(String(30))
    email = Column(String(150))
    description = Column(Text)
    open_time = Column(String(5), default="09:00")   # "HH:MM"
    close_time = Column(String(5), default="19:00")
    slot_duration = Column(Integer, default=30)       # minutos
    logo_url = Column(String(300))
