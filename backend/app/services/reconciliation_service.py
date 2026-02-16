"""
Reconciliation Service - PS1 Feature 1
Participation Reconciliation Intelligence Engine

Resolves conflicting participation data from multiple sources
and produces one authoritative participation status.
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, List, Optional
from datetime import datetime

from app.models.ticket import Ticket
from app.models.attendance import Attendance
from app.models.certificate import Certificate
from app.models.participation_role import ParticipationRole
from app.models.event import Event
from app.models.student import Student


class CanonicalStatus:
    """Canonical participation statuses as per PS1 requirements"""
    REGISTERED_ONLY = "REGISTERED_ONLY"
    ATTENDED_NO_CERTIFICATE = "ATTENDED_NO_CERTIFICATE"
    CERTIFIED = "CERTIFIED"
    INVALIDATED = "INVALIDATED"
    UNKNOWN = "UNKNOWN"


class ConflictType:
    """Types of conflicts that can be detected"""
    CERTIFICATE_WITHOUT_ATTENDANCE = "CERTIFICATE_WITHOUT_ATTENDANCE"
    CERTIFICATE_WITHOUT_REGISTRATION = "CERTIFICATE_WITHOUT_REGISTRATION"
    ATTENDANCE_WITHOUT_REGISTRATION = "ATTENDANCE_WITHOUT_REGISTRATION"
    MULTIPLE_SCANS_SAME_DAY = "MULTIPLE_SCANS_SAME_DAY"
    ADMIN_OVERRIDE_CONFLICT = "ADMIN_OVERRIDE_CONFLICT"
    REVOKED_CERTIFICATE_STILL_VALID = "REVOKED_CERTIFICATE_STILL_VALID"


class ReconciliationService:
    """
    Handles participation reconciliation and conflict detection
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_canonical_status(
        self, 
        event_id: int, 
        student_prn: str
    ) -> Dict:
        """
        Compute canonical participation status for a student in an event
        
        Returns:
            - canonical_status: REGISTERED_ONLY, ATTENDED_NO_CERTIFICATE, CERTIFIED, INVALIDATED
            - has_registration: bool
            - has_attendance: bool
            - has_certificate: bool
            - conflicts: list of conflicts
            - trust_score: 0-100 based on data quality
        """
        # Get registration (ticket)
        ticket = self.db.query(Ticket).filter_by(
            event_id=event_id,
            student_prn=student_prn
        ).first()
        
        # Get attendance (exclude invalidated records)
        attendance = self.db.query(Attendance).filter_by(
            event_id=event_id,
            student_prn=student_prn,
            invalidated=False  # PS1 Feature 4: Exclude invalidated attendance
        ).all()
        
        # Get certificate
        certificate = self.db.query(Certificate).filter_by(
            event_id=event_id,
            student_prn=student_prn
        ).first()
        
        # Get event for multi-day validation
        event = self.db.query(Event).filter_by(id=event_id).first()
        
        # Compute canonical status
        canonical_status = self._compute_status(
            ticket, attendance, certificate, event
        )
        
        # Detect conflicts
        conflicts = self._detect_conflicts(
            event_id, student_prn, ticket, attendance, certificate
        )
        
        # Compute trust score (0-100)
        trust_score = self._compute_trust_score(
            ticket, attendance, certificate, conflicts
        )
        
        return {
            "canonical_status": canonical_status,
            "has_registration": ticket is not None,
            "has_attendance": len(attendance) > 0,
            "has_certificate": certificate is not None and not certificate.revoked,
            "attendance_count": len(attendance),
            "days_attended": len(set([a.day_number for a in attendance])) if attendance else 0,
            "total_days_required": event.total_days if event else 1,
            "certificate_revoked": certificate.revoked if certificate else False,
            "conflicts": conflicts,
            "trust_score": trust_score,
            "raw_evidence": {
                "ticket_id": ticket.id if ticket else None,
                "attendance_ids": [a.id for a in attendance],
                "certificate_id": certificate.certificate_id if certificate else None
            }
        }
    
    def _compute_status(
        self, 
        ticket: Optional[Ticket],
        attendance: List[Attendance],
        certificate: Optional[Certificate],
        event: Optional[Event]
    ) -> str:
        """Compute the canonical status based on available data"""
        
        # Check for revoked certificate
        if certificate and certificate.revoked:
            return CanonicalStatus.INVALIDATED
        
        # Check if student has valid certificate
        if certificate and not certificate.revoked:
            return CanonicalStatus.CERTIFIED
        
        # Check if student attended
        if attendance:
            # For multi-day events, check if attended all days
            if event and event.total_days > 1:
                days_attended = len(set([a.day_number for a in attendance]))
                if days_attended >= event.total_days:
                    return CanonicalStatus.ATTENDED_NO_CERTIFICATE
                else:
                    # Partial attendance
                    return CanonicalStatus.ATTENDED_NO_CERTIFICATE
            else:
                return CanonicalStatus.ATTENDED_NO_CERTIFICATE
        
        # Only has registration
        if ticket:
            return CanonicalStatus.REGISTERED_ONLY
        
        # No data found
        return CanonicalStatus.UNKNOWN
    
    def _detect_conflicts(
        self,
        event_id: int,
        student_prn: str,
        ticket: Optional[Ticket],
        attendance: List[Attendance],
        certificate: Optional[Certificate]
    ) -> List[Dict]:
        """Detect conflicts in participation data"""
        conflicts = []
        
        # Conflict 1: Certificate without attendance
        if certificate and not certificate.revoked and not attendance:
            conflicts.append({
                "type": ConflictType.CERTIFICATE_WITHOUT_ATTENDANCE,
                "severity": "HIGH",
                "message": "Certificate issued but no attendance record found",
                "resolution": "Verify if attendance was recorded manually"
            })
        
        # Conflict 2: Certificate without registration
        if certificate and not certificate.revoked and not ticket:
            conflicts.append({
                "type": ConflictType.CERTIFICATE_WITHOUT_REGISTRATION,
                "severity": "MEDIUM",
                "message": "Certificate issued but no registration found",
                "resolution": "Check if student registered via alternate method"
            })
        
        # Conflict 3: Attendance without registration
        if attendance and not ticket:
            conflicts.append({
                "type": ConflictType.ATTENDANCE_WITHOUT_REGISTRATION,
                "severity": "LOW",
                "message": "Attendance recorded but no registration found",
                "resolution": "May be walk-in registration or manual entry"
            })
        
        # Conflict 4: Multiple scans same day
        if attendance:
            day_counts = {}
            for att in attendance:
                day = att.day_number or 1
                day_counts[day] = day_counts.get(day, 0) + 1
            
            for day, count in day_counts.items():
                if count > 1:
                    conflicts.append({
                        "type": ConflictType.MULTIPLE_SCANS_SAME_DAY,
                        "severity": "MEDIUM",
                        "message": f"Multiple scans detected on day {day} ({count} scans)",
                        "resolution": "Review scan logs for duplicate entries"
                    })
        
        # Conflict 5: Admin override vs QR scan
        if attendance:
            qr_scans = [a for a in attendance if a.scan_source == "qr_scan"]
            admin_overrides = [a for a in attendance if a.scan_source == "admin_override"]
            
            if qr_scans and admin_overrides:
                conflicts.append({
                    "type": ConflictType.ADMIN_OVERRIDE_CONFLICT,
                    "severity": "LOW",
                    "message": "Both QR scan and admin override recorded",
                    "resolution": "Verify which record is more reliable"
                })
        
        return conflicts
    
    def _compute_trust_score(
        self,
        ticket: Optional[Ticket],
        attendance: List[Attendance],
        certificate: Optional[Certificate],
        conflicts: List[Dict]
    ) -> int:
        """
        Compute trust score (0-100) based on data quality
        Higher score = more reliable data
        """
        score = 100
        
        # Deduct points for missing data
        if not ticket:
            score -= 10
        if not attendance:
            score -= 30
        
        # Deduct points for conflicts
        for conflict in conflicts:
            if conflict["severity"] == "HIGH":
                score -= 20
            elif conflict["severity"] == "MEDIUM":
                score -= 10
            else:
                score -= 5
        
        # Bonus for QR scans (more reliable than admin overrides)
        if attendance:
            qr_scans = [a for a in attendance if a.scan_source == "qr_scan"]
            score += min(len(qr_scans) * 5, 20)
        
        # Ensure score is in valid range
        return max(0, min(100, score))
    
    def get_event_conflicts(self, event_id: int) -> List[Dict]:
        """
        Get all conflicts for an entire event
        """
        # Get all students who have any participation record for this event
        tickets = self.db.query(Ticket.student_prn).filter_by(event_id=event_id).all()
        # Exclude invalidated attendance
        attendances = self.db.query(Attendance.student_prn).filter_by(
            event_id=event_id,
            invalidated=False
        ).distinct().all()
        certificates = self.db.query(Certificate.student_prn).filter_by(event_id=event_id).all()
        
        # Combine all student PRNs
        all_prns = set()
        all_prns.update([t.student_prn for t in tickets])
        all_prns.update([a.student_prn for a in attendances])
        all_prns.update([c.student_prn for c in certificates])
        
        # Get conflicts for each student
        event_conflicts = []
        for prn in all_prns:
            status_data = self.get_canonical_status(event_id, prn)
            if status_data["conflicts"]:
                event_conflicts.append({
                    "student_prn": prn,
                    "canonical_status": status_data["canonical_status"],
                    "conflicts": status_data["conflicts"],
                    "trust_score": status_data["trust_score"]
                })
        
        return event_conflicts
    
    def resolve_conflict(
        self,
        event_id: int,
        student_prn: str,
        resolution_action: str,
        reason: str,
        resolved_by: int
    ) -> Dict:
        """
        Mark a conflict as resolved with specific action
        
        resolution_action: 'ignore', 'fix_attendance', 'revoke_certificate', 'add_registration'
        """
        # This would update records based on resolution action
        # For now, return acknowledgment
        return {
            "event_id": event_id,
            "student_prn": student_prn,
            "resolution_action": resolution_action,
            "reason": reason,
            "resolved_by": resolved_by,
            "resolved_at": datetime.now().isoformat()
        }
