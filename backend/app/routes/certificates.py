from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import Dict

from app.db.database import get_db
from app.models.user import User
from app.models.event import Event
from app.core.permissions import require_organizer
from app.services.certificate_service import (
    issue_certificates,
    get_certificate_statistics,
    get_students_without_certificates
)
from app.services.audit_service import create_audit_log

router = APIRouter(prefix="/certificates", tags=["Certificates"])


@router.get("/event/{event_id}/stats")
def get_event_certificate_stats(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_organizer)
):
    """
    Get certificate statistics for an event
    Shows how many certificates have been issued and how many are pending
    """
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Check if user has access to this event
    if current_user.role != "ADMIN" and event.created_by != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to view certificates for this event"
        )
    
    stats = get_certificate_statistics(db, event_id)
    return stats


@router.get("/event/{event_id}/pending")
def get_pending_certificates(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_organizer)
):
    """
    Get list of students who are eligible for certificates but haven't received them yet
    """
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Check if user has access to this event
    if current_user.role != "ADMIN" and event.created_by != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to view certificates for this event"
        )
    
    students = get_students_without_certificates(db, event_id)
    return {
        "event_id": event_id,
        "pending_count": len(students),
        "students": students
    }


@router.post("/event/{event_id}/push")
def push_certificates(
    event_id: int,
    request: Request,
    dry_run: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_organizer)
):
    """
    Push certificates to all eligible students who haven't received one yet
    
    - Only sends to students who attended the event (have attendance records)
    - Skips students who already received certificates
    - If dry_run=True, returns who would receive certificates without actually sending
    
    Args:
        event_id: Event ID
        dry_run: If True, only preview who would get certificates without sending
    """
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Check if user has access to this event
    if current_user.role != "ADMIN" and event.created_by != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to push certificates for this event"
        )
    
    # Issue certificates
    result = issue_certificates(db, event_id, dry_run=dry_run)
    
    if not result.get("success"):
        raise HTTPException(
            status_code=500,
            detail=result.get("error", "Failed to issue certificates")
        )
    
    # Create audit log if not dry run and certificates were issued
    if not dry_run and result.get("certificates_issued", 0) > 0:
        create_audit_log(
            db=db,
            event_id=event_id,
            user_id=current_user.id,
            action_type="certificates_pushed",
            details={
                "total_eligible": result.get("total_eligible", 0),
                "certificates_issued": result.get("certificates_issued", 0),
                "emails_sent": result.get("emails_sent", 0),
                "emails_failed": result.get("emails_failed", 0)
            },
            ip_address=request.client.host if request.client else None
        )
    
    return result
