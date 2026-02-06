from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.responses import StreamingResponse
import csv
from io import StringIO

from app.db.database import get_db
from app.models.attendance import Attendance
from app.models.event import Event
from app.models.student import Student
from app.services.email_service import send_teacher_email

router = APIRouter(prefix="/export", tags=["Export"])

# Export Attendance CSV for an Event

@router.get("/attendance/event/{event_id}/csv")
def export_event_attendance_csv(
    event_id: int,
    db: Session = Depends(get_db)
):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    records = db.query(Attendance).filter(
        Attendance.event_id == event_id
    ).all()

    output = StringIO()
    writer = csv.writer(output)

    # CSV Header
    writer.writerow(["Student PRN", "Event ID", "Scanned At"])

    # Rows
    for r in records:
        writer.writerow([r.student_prn, r.event_id, r.scanned_at])

    output.seek(0)

    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={
            "Content-Disposition":
            f"attachment; filename=event_{event_id}_attendance.csv"
        }
    )
    
# Teacher Email API (actually sends email)

@router.post("/attendance/event/{event_id}/teacher")
def send_teacher_attendance(
    event_id: int,
    teacher_email: str,
    teacher_name: str = "Professor",
    db: Session = Depends(get_db)
):
    """
    Send attendance report email to teacher
    """
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    # Get all attendance records with student details
    records = db.query(Attendance, Student).join(
        Student, Attendance.student_prn == Student.prn
    ).filter(
        Attendance.event_id == event_id
    ).all()

    # Count total registered students (distinct PRNs who attended)
    # Using the Ticket table to get total registrations instead of attendance
    from app.models.ticket import Ticket
    total_registered = db.query(Ticket).filter(
        Ticket.event_id == event_id
    ).count()
    
    # If no tickets found, use attendance count
    if total_registered == 0:
        total_registered = len(records)

    attendance_list = [
        {
            "student_prn": attendance.student_prn,
            "student_name": student.name if student else "N/A",
            "scanned_at": attendance.scanned_at
        }
        for attendance, student in records
    ]

    # Format event date
    event_date = event.start_time.strftime('%B %d, %Y at %I:%M %p')
    
    # Send email
    success = send_teacher_email(
        to_email=teacher_email,
        teacher_name=teacher_name,
        event_title=event.title,
        event_location=event.location,
        event_date=event_date,
        total_registered=total_registered,
        total_present=len(attendance_list),
        attendance_list=attendance_list
    )
    
    if success:
        return {
            "success": True,
            "message": f"Attendance report sent to {teacher_email}",
            "teacher_email": teacher_email,
            "event_id": event_id,
            "event_title": event.title,
            "total_present": len(attendance_list),
            "total_registered": total_registered
        }
    else:
        raise HTTPException(
            status_code=500,
            detail="Failed to send email. Check SMTP configuration."
        )