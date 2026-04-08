from sqlalchemy import Column, Integer, String, Boolean, Text
from app.db.database import Base


class Professional(Base):
    __tablename__ = "professionals"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    specialty = Column(String(150))
    email = Column(String(150))
    phone = Column(String(30))
    bio = Column(Text)
    is_active = Column(Boolean, default=True)
    # Días laborables como string "0,1,2,3,4" (0=lunes, 6=domingo)
    working_days = Column(String(20), default="0,1,2,3,4")
    work_start = Column(String(5), default="09:00")
    work_end = Column(String(5), default="18:00")
