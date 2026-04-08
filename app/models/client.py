from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from app.db.database import Base


class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), index=True)
    phone = Column(String(30))
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
