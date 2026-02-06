from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.event import Event
from app.models.ticket import Ticket
from app.models.student import Student
from app.models.user import User
from app.schemas.ticket import TicketResponse
from app.security.jwt import create_ticket_token
from app.services.email_service import send_ticket_email
from app.core.permissions import require_organizer

router = APIRouter(prefix="/register", tags=["Registration"])


@router.post("/{event_id}", response_model=TicketResponse)
def register_for_event(
    event_id: int,
    student_prn: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_organizer)
):
    # 1. Check event exists
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    # 2. Prevent duplicate registration
    existing = db.query(Ticket).filter(
        Ticket.event_id == event_id,
        Ticket.student_prn == student_prn
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Already registered")

    # 3. Create JWT FIRST (ticket_id will be set after flush)
    temp_payload = {
        "event_id": event_id,
        "student_prn": student_prn
    }

    # 4. Create ticket WITHOUT committing yet
    ticket = Ticket(
        event_id=event_id,
        student_prn=student_prn,
        token="TEMP"  # placeholder to satisfy NOT NULL
    )

    db.add(ticket)
    db.flush()  # ✅ assigns ticket.id WITHOUT committing

    # 5. Now generate REAL token with ticket_id
    token = create_ticket_token({
        "ticket_id": ticket.id,
        "event_id": event_id,
        "student_prn": student_prn
    })

    ticket.token = token
    db.commit()
    db.refresh(ticket)

    # 6. Send ticket email to student
    student = db.query(Student).filter(Student.prn == student_prn).first()
    if student and student.email:
        try:
            send_ticket_email(
                to_email=student.email,
                student_name=student.name,
                event_title=event.title,
                event_location=event.location,
                event_start_time=event.start_time,
                event_end_time=event.end_time,
                ticket_token=token
            )
        except Exception as e:
            # Don't fail registration if email fails
            print(f"Warning: Failed to send ticket email: {str(e)}")
    
    print("JWT TOKEN:", token)
    return ticket