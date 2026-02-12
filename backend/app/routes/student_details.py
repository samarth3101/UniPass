from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.database import get_db
from app.models.student import Student
from app.models.attendance import Attendance
from app.models.event import Event
from app.models.ticket import Ticket
from app.models.user import User
from app.core.permissions import require_organizer
from typing import List, Dict, Any

router = APIRouter(prefix="/students", tags=["students"])


@router.get("/{prn}/analytics")
def get_student_analytics(
    prn: str, 
    db: Session = Depends(get_db),
    current_user: User = Depends(require_organizer)
):
    """
    Get detailed analytics for a student - requires ORGANIZER or ADMIN role
    
    Includes:
    - Student information
    - List of events registered for
    - Attendance history
    - Attendance statistics
    """
    # Get all tickets for this student first
    tickets = db.query(Ticket).filter(Ticket.student_prn == prn).all()
    
    # If no tickets exist, student doesn't exist in system
    if not tickets:
        raise HTTPException(status_code=404, detail="Student not found in system")
    
    # Get student info - create if doesn't exist
    student = db.query(Student).filter(Student.prn == prn).first()
    if not student:
        # Create placeholder student record from PRN
        student = Student(
            prn=prn,
            name=f"Student {prn}",  # Placeholder name
            email=None,
            branch=None,
            year=None,
            division=None
        )
        db.add(student)
        db.commit()
        db.refresh(student)
    
    # Get all attendance records
    attendance_records = (
        db.query(Attendance, Event, Ticket)
        .join(Ticket, Attendance.ticket_id == Ticket.id)
        .join(Event, Ticket.event_id == Event.id)
        .filter(Ticket.student_prn == prn)
        .order_by(Attendance.scanned_at.desc())
        .all()
    )
    
    # Format attendance history
    attendance_history = []
    for att, event, ticket in attendance_records:
        attendance_history.append({
            "attendance_id": att.id,
            "event_id": event.id,
            "event_title": event.title,
            "event_location": event.location,
            "event_start_time": event.start_time.isoformat() if event.start_time else None,
            "scanned_at": att.scanned_at.isoformat() if att.scanned_at else None,
        })
    
    # Get registered events (both attended and pending)
    registered_events = []
    for ticket in tickets:
        # Check if attendance exists for this ticket
        attendance = next((att for att, _, t in attendance_records if t.id == ticket.id), None)
        has_attendance = attendance is not None
        
        event = db.query(Event).filter(Event.id == ticket.event_id).first()
        if event:
            registered_events.append({
                "event_id": event.id,
                "event_title": event.title,
                "event_location": event.location,
                "event_start_time": event.start_time.isoformat() if event.start_time else None,
                "registered_at": ticket.issued_at.isoformat() if ticket.issued_at else None,
                "ticket_id": ticket.id,
                "token": ticket.token,
                "status": "completed" if has_attendance else "pending",
                "attended_at": attendance.scanned_at.isoformat() if has_attendance and attendance.scanned_at else None,
            })
    
    # Calculate statistics
    total_registered = len(tickets)
    total_attended = len(attendance_records)
    attendance_rate = (total_attended / total_registered * 100) if total_registered > 0 else 0
    
    # Get events by month for graph data
    monthly_stats = []
    if attendance_records:
        monthly_data = (
            db.query(
                func.to_char(Attendance.scanned_at, 'YYYY-MM').label('month'),
                func.count(Attendance.id).label('count')
            )
            .join(Ticket, Attendance.ticket_id == Ticket.id)
            .filter(Ticket.student_prn == prn)
            .group_by('month')
            .order_by('month')
            .all()
        )
        
        monthly_stats = [
            {"month": month, "count": count}
            for month, count in monthly_data
        ]
    
    return {
        "student": {
            "prn": student.prn,
            "name": student.name,
            "email": student.email,
            "branch": student.branch,
            "year": student.year,
            "division": student.division,
        },
        "statistics": {
            "total_registered": total_registered,
            "total_attended": total_attended,
            "attendance_rate": round(attendance_rate, 1),
            "events_missed": total_registered - total_attended,
        },
        "attendance_history": attendance_history,
        "registered_events": registered_events,
        "monthly_stats": monthly_stats,
    }


@router.get("/{prn}/event/{event_id}/attendance-status")
def get_student_event_attendance_status(
    prn: str,
    event_id: int,
    db: Session = Depends(get_db)
):
    """
    Public endpoint to check student's attendance status for a specific event.
    Returns:
    - Total days for the event
    - Days attended by student
    - Days remaining
    - Whether certificate is unlocked
    - Whether feedback is unlocked
    - List of days attended with timestamps
    """
    # Get event
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Get total days
    total_days = event.total_days or 1
    
    # Get all attendance records for this student and event
    attendance_records = db.query(Attendance).filter(
        Attendance.event_id == event_id,
        Attendance.student_prn == prn
    ).order_by(Attendance.day_number).all()
    
    # Count distinct days attended
    attended_days_count = db.query(
        func.count(func.distinct(Attendance.day_number))
    ).filter(
        Attendance.event_id == event_id,
        Attendance.student_prn == prn
    ).scalar()
    
    # Check if fully attended
    is_fully_attended = (attended_days_count >= total_days)
    
    # Format attendance details
    days_attended = [
        {
            "day_number": att.day_number,
            "scanned_at": att.scanned_at.isoformat() if att.scanned_at else None
        }
        for att in attendance_records
    ]
    
    return {
        "event_id": event_id,
        "event_title": event.title,
        "student_prn": prn,
        "total_days": total_days,
        "attended_days": attended_days_count or 0,
        "days_remaining": max(0, total_days - (attended_days_count or 0)),
        "certificate_unlocked": is_fully_attended,
        "feedback_unlocked": is_fully_attended,
        "is_fully_attended": is_fully_attended,
        "days_attended_details": days_attended,
        "progress_percentage": round((attended_days_count or 0) / total_days * 100, 1) if total_days > 0 else 0
    }
