"""
Volunteer Model
Tracks volunteers for events who receive certificates but don't have student accounts
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime, timezone


class Volunteer(Base):
    """
    Volunteers are external people who help with events
    They receive certificates but don't have student PRNs or login accounts
    """
    __tablename__ = "volunteers"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False, index=True)
    
    # Volunteer details
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, index=True)
    
    # Tracking
    added_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    added_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Certificate tracking
    certificate_sent = Column(Boolean, default=False)
    certificate_sent_at = Column(DateTime, nullable=True)
    
    # Relationships
    event = relationship("Event", foreign_keys=[event_id])
    added_by_user = relationship("User", foreign_keys=[added_by])
    
    # Unique constraint: one volunteer record per email per event
    __table_args__ = (
        {"sqlite_autoincrement": True},
    )
