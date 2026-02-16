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
    get_students_without_certificates,
    resend_failed_certificate_emails
)
from app.services.role_certificate_service import (
    issue_attendee_certificates,
    issue_organizer_certificates,
    issue_scanner_certificates,
    issue_volunteer_certificates
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


@router.post("/event/{event_id}/resend-failed")
def resend_failed_emails(
    event_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_organizer)
):
    """
    Resend certificate emails that previously failed
    Only sends to certificates where email_sent=False
    
    Useful when SMTP connection was down or timed out
    """
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Check if user has access to this event
    if current_user.role != "ADMIN" and event.created_by != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to resend certificates for this event"
        )
    
    # Resend failed emails
    result = resend_failed_certificate_emails(db, event_id)
    
    if not result.get("success"):
        raise HTTPException(
            status_code=500,
            detail=result.get("error", "Failed to resend certificate emails")
        )
    
    # Create audit log if any emails were sent
    if result.get("emails_sent", 0) > 0:
        create_audit_log(
            db=db,
            event_id=event_id,
            user_id=current_user.id,
            action_type="certificates_resent",
            details={
                "total_attempted": result.get("total_attempted", 0),
                "emails_sent": result.get("emails_sent", 0),
                "still_failed": result.get("still_failed", 0)
            },
            ip_address=request.client.host if request.client else None
        )
    
    return result


@router.get("/event/{event_id}/role-stats")
def get_role_certificate_stats(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_organizer)
):
    """
    Get certificate statistics for each role type
    Returns counts of eligible recipients for attendees, organizers, scanners, and volunteers
    """
    from app.models.attendance import Attendance
    from app.models.volunteer import Volunteer
    from app.models.certificate import Certificate
    
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Check if user has access to this event
    if current_user.role != "ADMIN" and event.created_by != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to view certificates for this event"
        )
    
    # Attendees: students who attended without certificates
    attendee_count = len(get_students_without_certificates(db, event_id))
    
    # Organizers: event creator (if no certificate exists for their email)
    creator = db.query(User).filter(User.id == event.created_by).first()
    organizer_count = 0
    if creator:
        organizer_exists = db.query(Certificate).filter(
            Certificate.event_id == event_id,
            Certificate.role_type == 'organizer',
            Certificate.recipient_email == creator.email
        ).first()
        organizer_count = 0 if organizer_exists else 1
    
    # Scanners: unique scanner IDs from attendance records without certificates
    scanner_ids = db.query(Attendance.scanner_id).filter(
        Attendance.event_id == event_id,
        Attendance.scanner_id.isnot(None)
    ).distinct().all()
    
    scanner_count = 0
    for scanner_id_tuple in scanner_ids:
        scanner_id = scanner_id_tuple[0]
        scanner = db.query(User).filter(User.id == scanner_id).first()
        if scanner:
            scanner_cert = db.query(Certificate).filter(
                Certificate.event_id == event_id,
                Certificate.role_type == 'scanner',
                Certificate.recipient_email == scanner.email
            ).first()
            if not scanner_cert:
                scanner_count += 1
    
    # Volunteers: volunteers without certificates
    volunteer_count = db.query(Volunteer).filter(
        Volunteer.event_id == event_id,
        Volunteer.certificate_sent == False
    ).count()
    
    return {
        "attendees": attendee_count,
        "organizers": organizer_count,
        "scanners": scanner_count,
        "volunteers": volunteer_count
    }


@router.post("/event/{event_id}/push-by-roles")
def push_certificates_by_roles(
    event_id: int,
    roles: Dict[str, bool],
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_organizer)
):
    """
    Push certificates to selected roles
    
    Request body format:
    {
        "attendees": true,
        "organizers": false,
        "scanners": true,
        "volunteers": true
    }
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
    
    results = {}
    total_issued = 0
    total_emailed = 0
    total_failed = 0
    
    # Issue attendee certificates
    if roles.get("attendees"):
        result = issue_attendee_certificates(db, event_id)
        results["attendees"] = result
        total_issued += result.get("issued", 0)
        total_emailed += result.get("emailed", 0)
        total_failed += result.get("failed", 0)
    
    # Issue organizer certificates
    if roles.get("organizers"):
        result = issue_organizer_certificates(db, event_id)
        results["organizers"] = result
        total_issued += result.get("issued", 0)
        total_emailed += result.get("emailed", 0)
        total_failed += result.get("failed", 0)
    
    # Issue scanner certificates
    if roles.get("scanners"):
        result = issue_scanner_certificates(db, event_id)
        results["scanners"] = result
        total_issued += result.get("issued", 0)
        total_emailed += result.get("emailed", 0)
        total_failed += result.get("failed", 0)
    
    # Issue volunteer certificates
    if roles.get("volunteers"):
        result = issue_volunteer_certificates(db, event_id)
        results["volunteers"] = result
        total_issued += result.get("issued", 0)
        total_emailed += result.get("emailed", 0)
        total_failed += result.get("failed", 0)
    
    # Create audit log
    if total_issued > 0:
        create_audit_log(
            db=db,
            event_id=event_id,
            user_id=current_user.id,
            action_type="role_certificates_pushed",
            details={
                "roles": roles,
                "total_issued": total_issued,
                "total_emailed": total_emailed,
                "total_failed": total_failed,
                "breakdown": results
            },
            ip_address=request.client.host if request.client else None
        )
    
    return {
        "success": True,
        "total_issued": total_issued,
        "total_emailed": total_emailed,
        "total_failed": total_failed,
        "breakdown": results
    }


@router.post("/event/{event_id}/resend-failed")
def resend_failed_certificates(
    event_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_organizer)
):
    """
    Resend certificate emails that failed to send
    Only resends emails for certificates where email_sent=False
    """
    from app.models.certificate import Certificate
    from app.models.event import Event
    from app.services.email_service import send_certificate_email
    from datetime import datetime, timezone
    
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Check if user has access to this event
    if current_user.role != "ADMIN" and event.created_by != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to resend certificates for this event"
        )
    
    # Get all certificates that failed to send email
    failed_certs = db.query(Certificate).filter(
        Certificate.event_id == event_id,
        Certificate.email_sent == False
    ).all()
    
    if not failed_certs:
        return {
            "success": True,
            "message": "No failed certificates to resend",
            "resent": 0,
            "still_failed": 0
        }
    
    resent = 0
    still_failed = 0
    
    for cert in failed_certs:
        try:
            # Determine recipient name and email
            if cert.recipient_name and cert.recipient_email:
                # Non-student certificate (organizer, scanner, volunteer)
                recipient_name = cert.recipient_name
                recipient_email = cert.recipient_email
            elif cert.student_prn:
                # Student certificate (attendee)
                from app.models.student import Student
                student = db.query(Student).filter(Student.prn == cert.student_prn).first()
                if not student or not student.email:
                    still_failed += 1
                    continue
                recipient_name = student.name
                recipient_email = student.email
            else:
                still_failed += 1
                continue
            
            # Send email
            event_date = event.start_time.strftime('%B %d, %Y') if event.start_time else 'TBD'
            success = send_certificate_email(
                to_email=recipient_email,
                student_name=recipient_name,
                event_title=event.title,
                event_location=event.location or 'TBD',
                event_date=event_date,
                certificate_id=cert.certificate_id,
                role_type=cert.role_type or 'attendee'
            )
            
            if success:
                cert.email_sent = True
                cert.email_sent_at = datetime.now(timezone.utc)
                resent += 1
            else:
                still_failed += 1
        
        except Exception as e:
            print(f"Error resending certificate {cert.certificate_id}: {e}")
            still_failed += 1
    
    db.commit()
    
    # Create audit log
    if resent > 0:
        create_audit_log(
            db=db,
            event_id=event_id,
            user_id=current_user.id,
            action_type="certificates_resent",
            details={
                "resent": resent,
                "still_failed": still_failed,
                "total_attempted": len(failed_certs)
            },
            ip_address=request.client.host if request.client else None
        )
    
    return {
        "success": True,
        "resent": resent,
        "still_failed": still_failed,
        "total_attempted": len(failed_certs)
    }
