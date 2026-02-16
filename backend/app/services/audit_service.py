"""
Audit Service - PS1 Feature 4
Change History & Audit Trail Engine

Provides consolidated view of all changes, corrections, and retroactive actions
for participation records.
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from app.models.audit_log import AuditLog
from app.models.certificate import Certificate
from app.models.attendance import Attendance
from app.models.user import User
from app.models.event import Event
from app.models.student import Student
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone

def create_audit_log(
    db: Session,
    event_id: int,
    user_id: Optional[int],
    action_type: str,
    details: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None
) -> AuditLog:
    """
    Create an audit log entry
    
    Action types:
    - event_created: Event was created
    - event_edited: Event details were modified
    - ticket_deleted: Registration ticket was deleted
    - override_used: Manual attendance override was used
    - qr_scanned: QR code was scanned for attendance
    - certificate_revoked: Certificate was revoked
    - attendance_invalidated: Attendance was marked invalid
    - participation_corrected: Manual correction applied
    """
    audit_log = AuditLog(
        event_id=event_id,
        user_id=user_id,
        action_type=action_type,
        details=details or {},
        ip_address=ip_address,
        timestamp=datetime.now(timezone.utc)
    )
    db.add(audit_log)
    db.commit()
    db.refresh(audit_log)
    return audit_log

def get_event_audit_logs(db: Session, event_id: int, limit: int = 100):
    """Get audit logs for a specific event, ordered by most recent first"""
    return db.query(AuditLog).filter(
        AuditLog.event_id == event_id
    ).order_by(AuditLog.timestamp.desc()).limit(limit).all()


class AuditService:
    """
    PS1 Feature 4: Comprehensive audit trail and change history
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_change_history(
        self, 
        event_id: int, 
        student_prn: str,
        limit: int = 50
    ) -> Dict:
        """
        Get comprehensive change history for a student in an event.
        Includes: certificate revocations, attendance invalidations, 
        manual corrections, and all audit log entries.
        """
        
        # Get student info
        student = self.db.query(Student).filter_by(prn=student_prn).first()
        
        # Get event info
        event = self.db.query(Event).filter_by(id=event_id).first()
        
        if not event:
            return {"error": "Event not found"}
        
        changes = []
        
        # 1. Get certificate revocations
        certificates = self.db.query(Certificate).filter_by(
            event_id=event_id,
            student_prn=student_prn,
            revoked=True
        ).all()
        
        for cert in certificates:
            revoker = self.db.query(User).filter_by(id=cert.revoked_by).first()
            changes.append({
                "timestamp": cert.revoked_at.isoformat() if cert.revoked_at else None,
                "action": "certificate_revoked",
                "action_type": "revocation",
                "performed_by": revoker.email if revoker else "Unknown",
                "performed_by_name": getattr(revoker, 'full_name', revoker.email) if revoker else "Unknown",
                "details": {
                    "certificate_id": cert.certificate_id,
                    "reason": cert.revocation_reason
                },
                "old_state": {"certificate_valid": True},
                "new_state": {"certificate_valid": False, "revoked": True}
            })
        
        # 2. Get attendance invalidations
        invalidated_attendance = self.db.query(Attendance).filter(
            and_(
                Attendance.event_id == event_id,
                Attendance.student_prn == student_prn,
                Attendance.invalidated == True
            )
        ).all()
        
        for att in invalidated_attendance:
            invalidator = self.db.query(User).filter_by(id=att.invalidated_by).first()
            changes.append({
                "timestamp": att.invalidated_at.isoformat() if att.invalidated_at else None,
                "action": "attendance_invalidated",
                "action_type": "invalidation",
                "performed_by": invalidator.email if invalidator else "Unknown",
                "performed_by_name": getattr(invalidator, 'full_name', invalidator.email) if invalidator else "Unknown",
                "details": {
                    "attendance_id": att.id,
                    "scan_date": att.scanned_at.isoformat() if att.scanned_at else None,
                    "day_number": att.day_number,
                    "reason": att.invalidation_reason
                },
                "old_state": {"attendance_valid": True},
                "new_state": {"attendance_valid": False, "invalidated": True}
            })
        
        # 3. Get audit log entries for this student
        audit_logs = self.db.query(AuditLog).filter_by(
            event_id=event_id
        ).order_by(desc(AuditLog.timestamp)).limit(limit).all()
        
        for log in audit_logs:
            if log.details and isinstance(log.details, dict):
                if log.details.get('student_prn') == student_prn:
                    user_obj = self.db.query(User).filter_by(id=log.user_id).first()
                    changes.append({
                        "timestamp": log.timestamp.isoformat() if log.timestamp else None,
                        "action": log.action_type,
                        "action_type": "audit",
                        "performed_by": user_obj.email if user_obj else "System",
                        "performed_by_name": getattr(user_obj, 'full_name', user_obj.email) if user_obj else "System",
                        "details": log.details,
                        "old_state": log.details.get('old_state', {}),
                        "new_state": log.details.get('new_state', {})
                    })
        
        # Sort all changes by timestamp (most recent first)
        changes.sort(key=lambda x: x['timestamp'] if x['timestamp'] else '', reverse=True)
        
        # Calculate summary
        summary = {
            "total_changes": len(changes),
            "revocations": sum(1 for c in changes if c['action_type'] == 'revocation'),
            "invalidations": sum(1 for c in changes if c['action_type'] == 'invalidation'),
            "corrections": sum(1 for c in changes if c['action'] == 'participation_corrected'),
            "audit_entries": sum(1 for c in changes if c['action_type'] == 'audit')
        }
        
        return {
            "student_info": {
                "prn": student_prn,
                "name": student.name if student else None,
                "email": student.email if student else None
            },
            "event_info": {
                "id": event.id,
                "title": event.title,
                "start_time": event.start_time.isoformat() if event.start_time else None
            },
            "changes": changes,
            "summary": summary
        }
    
    def get_event_audit_summary(self, event_id: int) -> Dict:
        """
        Get audit summary for entire event.
        Shows all changes across all students.
        """
        
        event = self.db.query(Event).filter_by(id=event_id).first()
        if not event:
            return {"error": "Event not found"}
        
        # Count certificate revocations
        revoked_certs = self.db.query(Certificate).filter_by(
            event_id=event_id,
            revoked=True
        ).count()
        
        # Count invalidated attendance
        invalidated_attendance_count = self.db.query(Attendance).filter(
            and_(
                Attendance.event_id == event_id,
                Attendance.invalidated == True
            )
        ).count()
        
        # Count audit log entries
        audit_entries = self.db.query(AuditLog).filter_by(
            event_id=event_id
        ).count()
        
        # Get recent changes
        recent_logs = self.db.query(AuditLog).filter_by(
            event_id=event_id
        ).order_by(desc(AuditLog.timestamp)).limit(10).all()
        
        recent_changes = []
        for log in recent_logs:
            user_obj = self.db.query(User).filter_by(id=log.user_id).first()
            recent_changes.append({
                "timestamp": log.timestamp.isoformat() if log.timestamp else None,
                "action": log.action_type,
                "performed_by": user_obj.email if user_obj else "System",
                "details": log.details
            })
        
        return {
            "event_id": event_id,
            "event_title": event.title,
            "summary": {
                "total_revocations": revoked_certs,
                "total_invalidations": invalidated_attendance_count,
                "total_audit_entries": audit_entries
            },
            "recent_changes": recent_changes
        }
    
    def log_correction(
        self,
        event_id: int,
        student_prn: str,
        user_id: int,
        correction_type: str,
        old_value: any,
        new_value: any,
        reason: str
    ):
        """
        Log a manual correction to participation data.
        Creates audit trail entry for trackability.
        """
        
        audit_log = AuditLog(
            event_id=event_id,
            user_id=user_id,
            action_type="participation_corrected",
            details={
                "student_prn": student_prn,
                "correction_type": correction_type,
                "reason": reason,
                "old_state": {"value": old_value},
                "new_state": {"value": new_value},
                "corrected_at": datetime.now(timezone.utc).isoformat()
            }
        )
        
        self.db.add(audit_log)
        self.db.commit()
        
        return audit_log
