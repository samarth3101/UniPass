from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime, timezone
import hashlib
import os
from enum import Enum

class CertificateRole(str, Enum):
    """Certificate role types"""
    ATTENDEE = "attendee"
    ORGANIZER = "organizer"
    SCANNER = "scanner"
    VOLUNTEER = "volunteer"

class Certificate(Base):
    """
    Track certificates issued to students/volunteers for events.
    Supports multiple role types with unique certificate designs.
    """
    __tablename__ = "certificates"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False, index=True)
    student_prn = Column(String, nullable=True, index=True)  # Nullable for volunteers
    
    # Certificate details
    certificate_id = Column(String, unique=True, index=True, nullable=False)  # Unique certificate identifier
    issued_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Role-based certificates
    role_type = Column(String, default="attendee", nullable=False, index=True)  # attendee, organizer, scanner, volunteer
    
    # For non-student certificates (volunteers, organizers, scanners)
    recipient_name = Column(String, nullable=True)
    recipient_email = Column(String, nullable=True)
    
    # Email delivery tracking
    email_sent = Column(Boolean, default=False)
    email_sent_at = Column(DateTime, nullable=True)
    
    # PS1 Feature 3: Verification System
    verification_hash = Column(String, unique=True, index=True, nullable=True)  # SHA-256 hash for verification
    
    # PS1 Feature 4: Revocation Support
    revoked = Column(Boolean, default=False)
    revoked_at = Column(DateTime, nullable=True)
    revoked_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    revocation_reason = Column(Text, nullable=True)
    
    # Relationship to Event
    event = relationship("Event", foreign_keys=[event_id])
    revoker = relationship("User", foreign_keys=[revoked_by])
    
    # Unique constraint: one certificate per student per event
    __table_args__ = (
        {"sqlite_autoincrement": True},
    )
    
    def generate_verification_hash(self, secret_key: str = None) -> str:
        """Generate SHA-256 hash for certificate verification"""
        if not secret_key:
            secret_key = os.getenv("SECRET_KEY", "default-secret-key")
        
        # Create unique string from certificate data
        data = f"{self.student_prn}:{self.event_id}:{self.certificate_id}:{self.issued_at.isoformat()}:{secret_key}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    def verify_hash(self, provided_hash: str, secret_key: str = None) -> bool:
        """Verify if provided hash matches the certificate"""
        expected_hash = self.generate_verification_hash(secret_key)
        return expected_hash == provided_hash
