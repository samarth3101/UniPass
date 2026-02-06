from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.db.base import Base   # ✅ FIXED

class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    student_prn = Column(String, nullable=False)

    token = Column(String, nullable=False)  # ✅ REQUIRED

    issued_at = Column(DateTime(timezone=True), server_default=func.now())