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
    
    # Check if event has started
    if event.start_time > datetime.utcnow():
        print(f"❌ Scan rejected: Event {event_id} hasn't started. Starts at {event.start_time}")
        raise HTTPException(
            status_code=403,
            detail=f"Event '{event.title}' has not started yet. It begins on {event.start_time.strftime('%d %b %Y, %I:%M %p')}."
        )
    
    # Check if event has ended (primary validation via end_time)
    if event.end_time and event.end_time < datetime.utcnow():
        print(f"❌ Scan rejected: Event {event_id} ended at {event.end_time}")
        raise HTTPException(
            status_code=403, 
            detail=f"Event '{event.title}' has already ended on {event.end_time.strftime('%d %b %Y, %I:%M %p')}. Attendance marking is closed. Contact admin for override."
        )
    
    # Calculate current event day (for multi-day events)
    # event.start_time is Day 1
    from datetime import date
    today = date.today()
    event_start_date = event.start_time.date()
    current_day = (today - event_start_date).days + 1
    
    # Get total days for the event (default: 1)
    total_days = event.total_days or 1
    
    # Day-based validation (secondary - only if no end_time or as a sanity check)
    # Allow some flexibility: if current_day is slightly over but end_time hasn't passed, allow it
    if not event.end_time and current_day > total_days:
        print(f"❌ Scan rejected: Event {event_id} completed. Current day: {current_day}, Total days: {total_days}")
        raise HTTPException(
            status_code=403,
            detail=f"Event '{event.title}' has already completed all {total_days} day(s). Attendance marking is closed."
        )
    
    # Check if already attended TODAY (prevent duplicate same-day scans)
    existing = db.query(Attendance).filter(
        Attendance.event_id == event_id,
        Attendance.student_prn == student_prn,
        Attendance.day_number == current_day
    ).first()
    
    if existing:
        # Get student info
        student = db.query(Student).filter(Student.prn == student_prn).first()
        
        # Calculate how many days attended so far
        from sqlalchemy import func
        attended_days = db.query(
            func.count(func.distinct(Attendance.day_number))
        ).filter(
            Attendance.event_id == event_id,
            Attendance.student_prn == student_prn
        ).scalar()
        
        return {
            "status": "already_scanned",
            "message": f"Already marked present for Day {current_day} at {existing.scanned_at.strftime('%I:%M %p')}",
            "attendance_id": existing.id,
            "student_name": student.name if student else "Unknown",
            "scanned_at": existing.scanned_at.isoformat(),
            "current_day": current_day,
            "total_days": total_days,
            "attended_days": attended_days,
            "days_remaining": total_days - attended_days
        }
    
    # Create new attendance record with day_number
    attendance = Attendance(
        ticket_id=ticket_id,
        event_id=event_id,
        student_prn=student_prn,
        day_number=current_day,
        scan_source="qr_scan",
        scanner_id=current_user.id if current_user else None,
        device_info=request.headers.get("User-Agent")
    )

    db.add(attendance)
    db.commit()
    db.refresh(attendance)
    
    # Get student info
    student = db.query(Student).filter(Student.prn == student_prn).first()
    
    # Calculate how many days attended so far (including this scan)
    from sqlalchemy import func
    attended_days = db.query(
        func.count(func.distinct(Attendance.day_number))
    ).filter(
        Attendance.event_id == event_id,
        Attendance.student_prn == student_prn
    ).scalar()
    
    # Determine if certificate and feedback are unlocked
    is_fully_attended = (attended_days == total_days)
    
    # Audit log: QR code scanned
    create_audit_log(
        db=db,
        event_id=event_id,
        user_id=current_user.id if current_user else None,
        action_type="qr_scanned",
        details={
            "student_prn": student_prn,
            "student_name": student.name if student else "Unknown",
            "ticket_id": ticket_id,
            "day_number": current_day,
            "attended_days": attended_days,
            "total_days": total_days
        },
        ip_address=request.client.host if request.client else None
    )
    
    # Broadcast to live monitors
    broadcast_scan_event(event_id, {
        "type": "new_scan",
        "prn": student_prn,
        "name": student.name if student else "Unknown",
        "time": attendance.scanned_at.strftime("%H:%M:%S"),
        "day": current_day
    })

    return {
        "status": "success",
        "message": f"Attendance marked for Day {current_day}/{total_days}",
        "attendance_id": attendance.id,
        "student_prn": student_prn,
        "student_name": student.name if student else "Unknown",
        "event_id": event_id,
        "scanned_at": attendance.scanned_at.isoformat(),
        "current_day": current_day,
        "total_days": total_days,
        "attended_days": attended_days,
        "days_remaining": total_days - attended_days,
        "certificate_unlocked": is_fully_attended,
        "feedback_unlocked": is_fully_attended,
        "completion_message": "🎉 Congratulations! You attended all days. Certificate and feedback are now available!" if is_fully_attended else f"Keep going! {total_days - attended_days} more day(s) to unlock certificate."
    }