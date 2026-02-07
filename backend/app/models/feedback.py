from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime, timezone

class Feedback(Base):
    """
    Store feedback from students who attended events.
    AI-ready with sentiment fields for ML processing.
    """
    __tablename__ = "feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False, index=True)
    student_prn = Column(String, nullable=False, index=True)
    
    # Feedback content
    overall_rating = Column(Integer, nullable=False)  # 1-5 stars
    content_quality = Column(Integer, nullable=False)  # 1-5
    organization_rating = Column(Integer, nullable=False)  # 1-5
    venue_rating = Column(Integer, nullable=False)  # 1-5
    speaker_rating = Column(Integer, nullable=True)  # 1-5 (optional if no speaker)
    
    # Text feedback (AI-ready)
    what_liked = Column(Text, nullable=True)  # What did you like most?
    what_improve = Column(Text, nullable=True)  # What can be improved?
    additional_comments = Column(Text, nullable=True)  # Any other comments?
    
    # Would recommend
    would_recommend = Column(Boolean, nullable=False, default=True)
    
    # AI processing fields
    sentiment_score = Column(Integer, nullable=True)  # -1 (negative), 0 (neutral), 1 (positive)
    ai_summary = Column(Text, nullable=True)  # AI-generated summary
    
    # Metadata
    submitted_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    event = relationship("Event", foreign_keys=[event_id])
    
    __table_args__ = (
        {"sqlite_autoincrement": True},
    )
