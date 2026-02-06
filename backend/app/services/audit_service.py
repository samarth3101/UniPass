from sqlalchemy.orm import Session
from app.models.audit_log import AuditLog
from typing import Optional, Dict, Any
from datetime import datetime

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
    """
    audit_log = AuditLog(
        event_id=event_id,
        user_id=user_id,
        action_type=action_type,
        details=details or {},
        ip_address=ip_address,
        timestamp=datetime.utcnow()
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
