from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum, Boolean, Text
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime, timezone
from enum import Enum

class ScanSource(str, Enum):
    """Track how attendance was recorded"""
    QR_SCAN = "qr_scan"  # Match database enum values
    ADMIN_OVERRIDE = "admin_override"
    BULK_UPLOAD = "bulk_upload"
    API_INTEGRATION = "api_integration"

class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, index=True)
    event_id = Column(Integer, index=True)
    student_prn = Column(String, index=True)
    scanned_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)  # Indexed for time analysis
    
    # Multi-Day Event Support
    day_number = Column(Integer, nullable=True)  # Which day of the event (1, 2, 3, etc.)
    
    # AI Readiness Phase 0 fields - Scan tracking for data quality
    # Use native=False to store as VARCHAR instead of PostgreSQL enum
    scan_source = Column(String, default="qr_scan", nullable=False)
    scanner_id = Column(Integer, ForeignKey('users.id'), nullable=True)  # Who performed scan
    device_info = Column(String, nullable=True)  # Browser/device fingerprint
    
    # PS1 Feature 4: Retroactive Change Support (Attendance Invalidation)
    invalidated = Column(Boolean, default=False, nullable=False)  # Mark attendance as invalid
    invalidated_at = Column(DateTime, nullable=True)  # When was it invalidated
    invalidated_by = Column(Integer, ForeignKey('users.id'), nullable=True)  # Who invalidated it
    invalidation_reason = Column(Text, nullable=True)  # Reason for invalidation
    
    # Relationships
    scanner = relationship("User", foreign_keys=[scanner_id])
    invalidator = relationship("User", foreign_keys=[invalidated_by])