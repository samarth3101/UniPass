from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum
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
    
    # AI Readiness Phase 0 fields - Scan tracking for data quality
    # Use native=False to store as VARCHAR instead of PostgreSQL enum
    scan_source = Column(String, default="qr_scan", nullable=False)
    scanner_id = Column(Integer, ForeignKey('users.id'), nullable=True)  # Who performed scan
    device_info = Column(String, nullable=True)  # Browser/device fingerprint