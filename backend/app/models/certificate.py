from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime, timezone

class Certificate(Base):
    """
    Track certificates issued to students for attending events.
    Ensures certificates are sent only once per student per event.
    """
    __tablename__ = "certificates"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False, index=True)
    student_prn = Column(String, nullable=False, index=True)
    
    # Certificate details
    certificate_id = Column(String, unique=True, index=True, nullable=False)  # Unique certificate identifier
    issued_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Email delivery tracking
    email_sent = Column(Boolean, default=False)
    email_sent_at = Column(DateTime, nullable=True)
    
    # Relationship to Event
    event = relationship("Event", foreign_keys=[event_id])
    
    # Unique constraint: one certificate per student per event
    __table_args__ = (
        {"sqlite_autoincrement": True},
    )
