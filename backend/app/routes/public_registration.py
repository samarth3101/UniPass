from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.event import Event
from app.models.ticket import Ticket
from app.models.student import Student
from app.security.jwt import create_ticket_token
from app.services.email_service import send_ticket_email

router = APIRouter(prefix="/register/slug", tags=["Public Registration"])


@router.post("/{share_slug}")
def register_student(
    share_slug: str,
    prn: str,
    name: str,
    background_tasks: BackgroundTasks,
    email: str | None = None,
    branch: str | None = None,
    year: int | None = None,
    division: str | None = None,
    db: Session = Depends(get_db)
):
    # 1. Find event by slug
    event = db.query(Event).filter(Event.share_slug == share_slug).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    # 2. Create or update student record
    student = db.query(Student).filter(Student.prn == prn).first()
    if student:
        # Update existing student info
        student.name = name
        student.email = email
        student.branch = branch
        student.year = year
        student.division = division
    else:
        # Create new student
        student = Student(
            prn=prn,
            name=name,
            email=email,
            branch=branch,
            year=year,
            division=division
        )
        db.add(student)
    
    db.flush()  # Save student first

    # 3. Check for duplicate registration - return existing ticket instead of error
    existing = db.query(Ticket).filter(
        Ticket.event_id == event.id,
        Ticket.student_prn == prn
    ).first()
    if existing:
        # Return existing ticket data with student and event info
        return {
            "ticket_id": existing.id,
            "token": existing.token,
            "already_registered": True,
            "message": "You are already registered for this event",
            "student": {
                "prn": student.prn,
                "name": student.name,
                "email": student.email,
                "branch": student.branch,
                "year": student.year,
                "division": student.division,
            },
            "event": {
                "id": event.id,
                "title": event.title,
                "description": event.description,
                "location": event.location,
                "start_time": event.start_time.isoformat() if event.start_time else None,
                "end_time": event.end_time.isoformat() if event.end_time else None,
            }
        }

    # 4. Create ticket with TEMP token
    ticket = Ticket(
        event_id=event.id,
        student_prn=prn,
        token="TEMP"  # important
    )

    db.add(ticket)
    db.flush()  # ✅ ticket.id generated here

    # 5. Generate JWT with real ticket_id
    token = create_ticket_token({
        "ticket_id": ticket.id,
        "event_id": event.id,
        "student_prn": prn
    })

    ticket.token = token
    db.commit()
    db.refresh(ticket)

    # 6. Send ticket email to student in background (non-blocking)
    if email:
        background_tasks.add_task(
            send_ticket_email,
            to_email=email,
            student_name=name,
            event_title=event.title,
            event_location=event.location,
            event_start_time=event.start_time,
            event_end_time=event.end_time,
            ticket_token=token
        )

    # 7. Return ticket with full event and student details
    return {
        "message": "Registration successful",
        "ticket_id": ticket.id,
        "token": token,
        "student": {
            "prn": prn,
            "name": name,
            "email": email,
            "branch": branch,
            "year": year,
            "division": division
        },
        "event": {
            "id": event.id,
            "title": event.title,
            "description": event.description,
            "location": event.location,
            "start_time": event.start_time.isoformat() if event.start_time else None,
            "end_time": event.end_time.isoformat() if event.end_time else None
        }
    }