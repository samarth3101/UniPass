from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime, timezone


class LectureReport(Base):
    """
    AI-generated lecture intelligence reports
    Stores audio transcripts, keywords, and structured summaries
    """
    __tablename__ = "lecture_reports"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False, index=True)
    audio_filename = Column(String, nullable=False)  # Original audio file name
    transcript = Column(Text, nullable=True)  # Full speech-to-text transcript
    keywords = Column(JSON, nullable=True)  # Extracted keywords as JSON array
    summary = Column(Text, nullable=True)  # AI-generated structured summary (JSON string)
    generated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    generated_by = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Processing status tracking
    status = Column(String, default="processing", nullable=False)  # processing, completed, failed
    error_message = Column(Text, nullable=True)  # Error details if processing failed
    
    # Relationships
    event = relationship("Event", backref="lecture_reports")
    creator = relationship("User", foreign_keys=[generated_by])
