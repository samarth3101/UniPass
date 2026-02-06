from sqlalchemy import Column, Integer, String, DateTime
from app.db.base import Base
from datetime import datetime, timezone

class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, index=True)
    event_id = Column(Integer, index=True)
    student_prn = Column(String, index=True)
    scanned_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))