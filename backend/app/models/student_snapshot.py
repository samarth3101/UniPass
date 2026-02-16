"""
Student Snapshot Model
Captures historical state of student profile at registration time
Enables "as-of" queries for retroactive analysis
"""

from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base import Base


class StudentSnapshot(Base):
    """
    Immutable snapshot of student data at a specific point in time
    Created automatically when student registers for an event
    """
    __tablename__ = "student_snapshots"
    
    id = Column(Integer, primary_key=True, index=True)
    student_prn = Column(String, nullable=False, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    
    # Snapshot metadata
    captured_at = Column(DateTime, default=datetime.now, nullable=False)
    snapshot_trigger = Column(String, nullable=False)  # "registration", "manual", "scheduled"
    
    # Student profile at capture time
    profile_data = Column(JSON, nullable=False)  # Full student profile as JSON
    """
    profile_data structure:
    {
        "prn": "PRN001",
        "name": "John Doe",
        "email": "john@example.com",
        "department": "Computer Science",
        "year": 3,
        "phone": "1234567890",
        "custom_fields": {...}
    }
    """
    
    # Participation status at capture time
    participation_status = Column(JSON, nullable=True)
    """
    participation_status structure:
    {
        "total_events": 10,
        "attended_events": 8,
        "certificates_earned": 7,
        "roles_held": ["PARTICIPANT", "VOLUNTEER"],
        "last_participation": "2026-01-15T10:30:00"
    }
    """
    
    # Relationships
    event = relationship("Event", back_populates="student_snapshots")
    
    # Indexes for efficient querying
    __table_args__ = (
        Index('ix_snapshot_student_event', 'student_prn', 'event_id'),
        Index('ix_snapshot_captured_at', 'captured_at'),
    )
    
    def __repr__(self):
        return f"<StudentSnapshot(prn={self.student_prn}, event={self.event_id}, captured={self.captured_at})>"


# Update Event model to include relationship (add this to app/models/event.py)
# student_snapshots = relationship("StudentSnapshot", back_populates="event", cascade="all, delete-orphan")
