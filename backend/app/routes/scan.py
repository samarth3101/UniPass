from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.db.database import get_db
from app.security.jwt import decode_ticket_token
from app.models.attendance import Attendance
from app.models.ticket import Ticket
from app.models.student import Student
from app.models.event import Event
from app.models.user import User
from app.core.permissions import get_current_user_optional
from app.services.audit_service import create_audit_log
from app.routes.monitor import broadcast_scan_event
from datetime import datetime

router = APIRouter(prefix="/scan", tags=["Scan & Attendance"])
limiter = Limiter(key_func=get_remote_address)


@router.post("/")
@limiter.limit("30/minute")  # Limit scan attempts per minute
def scan_qr(
    token: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """Scan a ticket QR code and mark attendance"""
    
    # Decode and validate the JWT token
    try:
        payload = decode_ticket_token(token)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
    
    ticket_id = payload.get("ticket_id")
    event_id = payload.get("event_id")
    student_prn = payload.get("student_prn")
    
    if not all([ticket_id, event_id, student_prn]):
        raise HTTPException(status_code=400, detail="Invalid token payload")
    
    # Verify the ticket exists and matches
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    if ticket.event_id != event_id or ticket.student_prn != student_prn:
        raise HTTPException(status_code=400, detail="Token mismatch with ticket")
    
    # Check if event has ended
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    if event.end_time and event.end_time < datetime.utcnow():
        raise HTTPException(
            status_code=403, 
            detail=f"Event '{event.title}' has already ended on {event.end_time.strftime('%d %b %Y, %I:%M %p')}. Attendance marking is closed. Contact admin for override."
        )
    
    # Check if already attended (prevent duplicate scans)
    existing = db.query(Attendance).filter(
        Attendance.ticket_id == ticket_id,
        Attendance.event_id == event_id
    ).first()
    
    if existing:
        # Get student info
        student = db.query(Student).filter(Student.prn == student_prn).first()
        return {
            "status": "already_scanned",
            "message": f"Already marked present at {existing.scanned_at}",
            "attendance_id": existing.id,
            "student_name": student.name if student else "Unknown",
            "scanned_at": existing.scanned_at.isoformat()
        }
    
    # Create new attendance record
    attendance = Attendance(
        ticket_id=ticket_id,
        event_id=event_id,
        student_prn=student_prn
    )

    db.add(attendance)
    db.commit()
    db.refresh(attendance)
    
    # Get student info
    student = db.query(Student).filter(Student.prn == student_prn).first()
    
    # Audit log: QR code scanned
    create_audit_log(
        db=db,
        event_id=event_id,
        user_id=current_user.id if current_user else None,
        action_type="qr_scanned",
        details={
            "student_prn": student_prn,
            "student_name": student.name if student else "Unknown",
            "ticket_id": ticket_id
        },
        ip_address=request.client.host if request.client else None
    )
    
    # Broadcast to live monitors
    broadcast_scan_event(event_id, {
        "type": "new_scan",
        "prn": student_prn,
        "name": student.name if student else "Unknown",
        "time": attendance.scanned_at.strftime("%H:%M:%S")
    })

    return {
        "status": "success",
        "message": "Attendance marked successfully",
        "attendance_id": attendance.id,
        "student_prn": student_prn,
        "student_name": student.name if student else "Unknown",
        "event_id": event_id,
        "scanned_at": attendance.scanned_at.isoformat()
    }