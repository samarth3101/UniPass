from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict
from datetime import datetime

from app.db.database import get_db
from app.models.attendance import Attendance
from app.models.event import Event
from app.models.ticket import Ticket
from app.models.student import Student
from app.models.user import User
from app.schemas.attendance_dashboard import AttendanceItem, AttendanceSummary
from app.core.permissions import require_organizer, require_admin

router = APIRouter(
    prefix="/attendance",
    tags=["Attendance Dashboard"]
)

# ==============================
# API 1: Get Attendance List for an Event
# ==============================
@router.get(
    "/event/{event_id}",
    response_model=List[AttendanceItem]
)
def get_event_attendance(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_organizer)
):
    """Get attendance list for event - requires ORGANIZER or ADMIN role"""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    attendance = db.query(Attendance).filter(
        Attendance.event_id == event_id
    ).all()

    return attendance


# ==============================
# API 2: Attendance Summary (Enhanced)
# ==============================
@router.get(
    "/event/{event_id}/summary",
    response_model=AttendanceSummary
)
def get_attendance_summary(
    event_id: int,
    db: Session = Depends(get_db)
):
    # Get total registered (tickets created for this event)
    total_registered = db.query(Ticket).filter(
        Ticket.event_id == event_id
    ).count()
    
    # Get unique students who attended (scanned their tickets)
    total_attended = db.query(func.count(func.distinct(Attendance.student_prn))).filter(
        Attendance.event_id == event_id
    ).scalar()

    return {
        "event_id": event_id,
        "total_registered": total_registered,
        "total_attended": total_attended,
        "total_present": total_attended  # Backward compatibility
    }


# ==============================
# API 2.5: Bulk Attendance Summary (OPTIMIZED FOR DASHBOARD)
# ==============================
@router.get(
    "/summary/bulk",
    response_model=Dict[int, AttendanceSummary]
)
def get_bulk_attendance_summary(
    db: Session = Depends(get_db)
):
    """
    Get attendance summary for ALL events in a single query.
    This is optimized for dashboard loading to avoid N+1 query problem.
    
    Returns:
        Dictionary mapping event_id to attendance summary
    """
    # Get all registrations grouped by event
    registrations = db.query(
        Ticket.event_id,
        func.count(Ticket.id).label('total_registered')
    ).group_by(Ticket.event_id).all()
    
    # Get all attendance grouped by event
    attendance = db.query(
        Attendance.event_id,
        func.count(func.distinct(Attendance.student_prn)).label('total_attended')
    ).group_by(Attendance.event_id).all()
    
    # Build lookup dictionaries
    reg_dict = {r.event_id: r.total_registered for r in registrations}
    att_dict = {a.event_id: a.total_attended for a in attendance}
    
    # Get all event IDs
    all_event_ids = set(reg_dict.keys()) | set(att_dict.keys())
    
    # Build response
    result = {}
    for event_id in all_event_ids:
        total_reg = reg_dict.get(event_id, 0)
        total_att = att_dict.get(event_id, 0)
        result[event_id] = {
            "event_id": event_id,
            "total_registered": total_reg,
            "total_attended": total_att,
            "total_present": total_att  # Backward compatibility
        }
    
    return result


# ==============================
# API 3: Student-wise Attendance
# ==============================
@router.get(
    "/student/{student_prn}",
    response_model=List[AttendanceItem]
)
def get_student_attendance(
    student_prn: str,
    db: Session = Depends(get_db)
):
    records = db.query(Attendance).filter(
        Attendance.student_prn == student_prn
    ).all()

    return records


# ==============================
# API 4: Get Registered Students for Event
# ==============================
@router.get("/event/{event_id}/registered")
def get_registered_students(
    event_id: int,
    db: Session = Depends(get_db)
):
    """Get all students who registered (have tickets) for this event"""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Get all tickets for this event with student info
    tickets = db.query(Ticket).filter(Ticket.event_id == event_id).all()
    
    registered_students = []
    for ticket in tickets:
        # Get student details
        student = db.query(Student).filter(Student.prn == ticket.student_prn).first()
        
        # Check if attended
        attended = db.query(Attendance).filter(
            Attendance.event_id == event_id,
            Attendance.student_prn == ticket.student_prn
        ).first()
        
        registered_students.append({
            "ticket_id": ticket.id,
            "prn": ticket.student_prn,
            "name": student.name if student else "Unknown",
            "email": student.email if student else None,
            "branch": student.branch if student else None,
            "year": student.year if student else None,
            "division": student.division if student else None,
            "registered_at": ticket.issued_at.isoformat() if ticket.issued_at else None,
            "attended": attended is not None,
            "scanned_at": attended.scanned_at.isoformat() if attended else None
        })
    
    return {
        "event_id": event_id,
        "total": len(registered_students),
        "students": registered_students
    }


# ==============================
# API 5: Get Attended Students for Event
# ==============================
@router.get("/event/{event_id}/attended")
def get_attended_students(
    event_id: int,
    db: Session = Depends(get_db)
):
    """Get all students who actually attended (scanned) this event"""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Get all attendance records for this event
    attendance_records = db.query(Attendance).filter(
        Attendance.event_id == event_id
    ).all()
    
    attended_students = []
    seen_prns = set()
    
    for record in attendance_records:
        # Avoid duplicates (in case someone scanned multiple times)
        if record.student_prn in seen_prns:
            continue
        seen_prns.add(record.student_prn)
        
        # Get student details
        student = db.query(Student).filter(Student.prn == record.student_prn).first()
        
        attended_students.append({
            "attendance_id": record.id,
            "prn": record.student_prn,
            "name": student.name if student else "Unknown",
            "email": student.email if student else None,
            "branch": student.branch if student else None,
            "year": student.year if student else None,
            "division": student.division if student else None,
            "scanned_at": record.scanned_at.isoformat() if record.scanned_at else None
        })
    
    return {
        "event_id": event_id,
        "total": len(attended_students),
        "students": attended_students
    }# ==============================
# API 6: Override Attendance (Admin Only)
# ==============================
@router.post("/event/{event_id}/override")
def override_attendance(
    event_id: int,
    student_prn: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Manually mark attendance for a student even if event has ended.
    Used by admin staff to fix genuine attendance issues.
    Requires ADMIN role only.
    """
    # Verify event exists
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Verify student has a ticket for this event
    ticket = db.query(Ticket).filter(
        Ticket.event_id == event_id,
        Ticket.student_prn == student_prn
    ).first()
    
    if not ticket:
        raise HTTPException(
            status_code=404, 
            detail=f"No ticket found for student {student_prn} in event '{event.title}'"
        )
    
    # Check if already attended
    existing = db.query(Attendance).filter(
        Attendance.ticket_id == ticket.id,
        Attendance.event_id == event_id
    ).first()
    
    if existing:
        return {
            "status": "already_marked",
            "message": "Attendance was already marked",
            "attendance_id": existing.id,
            "scanned_at": existing.scanned_at.isoformat()
        }
    
    # Create attendance record with override flag
    attendance = Attendance(
        ticket_id=ticket.id,
        event_id=event_id,
        student_prn=student_prn,
        scanned_at=datetime.utcnow()  # Mark with current time
    )
    
    db.add(attendance)
    db.commit()
    db.refresh(attendance)
    
    # Get student info
    student = db.query(Student).filter(Student.prn == student_prn).first()
    
    return {
        "status": "success",
        "message": f"Attendance marked via override for {student.name if student else student_prn}",
        "attendance_id": attendance.id,
        "student_prn": student_prn,
        "student_name": student.name if student else "Unknown",
        "scanned_at": attendance.scanned_at.isoformat(),
        "override": True
    }
