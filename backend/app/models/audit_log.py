from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.base import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    action_type = Column(String(50), nullable=False, index=True)  # event_created, event_edited, ticket_deleted, override_used, qr_scanned
    details = Column(JSON, nullable=True)  # Additional context (e.g., what was changed, ticket PRN, etc.)
    ip_address = Column(String(45), nullable=True)  # Support IPv4 and IPv6
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True)

    # Relationships
    event = relationship("Event", back_populates="audit_logs")
    user = relationship("User")
