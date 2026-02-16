from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime, timezone
from enum import Enum

class RoleType(str, Enum):
    """Event-level participation roles"""
    PARTICIPANT = "PARTICIPANT"
    VOLUNTEER = "VOLUNTEER"
    SPEAKER = "SPEAKER"
    ORGANIZER = "ORGANIZER"
    JUDGE = "JUDGE"
    MENTOR = "MENTOR"

class ParticipationRole(Base):
    """
    Track event-specific roles for students.
    A student can have multiple roles per event or across events.
    """
    __tablename__ = "participation_roles"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False, index=True)
    student_prn = Column(String, nullable=False, index=True)
    role = Column(SQLEnum(RoleType), nullable=False, default=RoleType.PARTICIPANT)
    
    # When role was assigned
    assigned_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    assigned_by = Column(Integer, ForeignKey("users.id"), nullable=True)  # Who assigned this role
    
    # Optional time segment for role (e.g., "Day 1: 9AM-12PM")
    time_segment = Column(String, nullable=True)
    
    # Relationship to Event
    event = relationship("Event", foreign_keys=[event_id])
    assigner = relationship("User", foreign_keys=[assigned_by])
    
    __table_args__ = (
        {"sqlite_autoincrement": True},
    )
