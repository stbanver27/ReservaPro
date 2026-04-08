from sqlalchemy import Column, Integer, String, Float, Boolean, Text
from app.db.database import Base


class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    description = Column(Text)
    duration_minutes = Column(Integer, nullable=False, default=30)
    price = Column(Float, nullable=False, default=0.0)
    is_active = Column(Boolean, default=True)
