from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime, timezone

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    location = Column(String)
    start_time = Column(DateTime, index=True)  # Indexed for AI time-based queries
    end_time = Column(DateTime)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)  # Track event creator
    
    share_slug = Column(String, unique=True, index=True, nullable=False)
    
    # AI Readiness Phase 0 fields
    event_type = Column(String, nullable=True, index=True)  # workshop, seminar, hackathon, etc.
    capacity = Column(Integer, nullable=True)  # Max attendees for attendance rate calculations
    department = Column(String, nullable=True, index=True)  # CS, IT, ENTC, etc.
    
    # Multi-Day Event Support
    total_days = Column(Integer, default=1, nullable=False)  # Number of days event spans (default: 1)
    
    # Relationship to User
    creator = relationship("User", foreign_keys=[created_by])
    
    # Relationship to AuditLogs
    audit_logs = relationship("AuditLog", back_populates="event", cascade="all, delete-orphan")