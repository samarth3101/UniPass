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
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)  # Track event creator
    
    share_slug = Column(String, unique=True, index=True, nullable=False)
    
    # Relationship to User
    creator = relationship("User", foreign_keys=[created_by])
    
    # Relationship to AuditLogs
    audit_logs = relationship("AuditLog", back_populates="event", cascade="all, delete-orphan")