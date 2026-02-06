import uuid
from slugify import slugify
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.event import Event
from app.models.user import User
from app.schemas.event import EventCreate, EventResponse, EventsPaginatedResponse
from app.schemas.audit_log import AuditLogResponse
from app.core.permissions import require_organizer
from app.services.audit_service import create_audit_log, get_event_audit_logs
from app.services.report_service import generate_event_report_pdf

router = APIRouter(prefix="/events", tags=["Events"])


def generate_share_slug(title: str) -> str:
    return f"{slugify(title)}-{uuid.uuid4().hex[:6]}"


@router.post("/", response_model=EventResponse)
def create_event(
    event: EventCreate, 
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_organizer)
):
    """Create new event - requires ORGANIZER or ADMIN role"""
    # Ensure times are in UTC for storage
    from datetime import timezone as tz
    start_time = event.start_time
    end_time = event.end_time
    
    # If timezone-aware, convert to UTC; if naive, assume UTC
    if start_time.tzinfo is not None:
        start_time = start_time.astimezone(tz.utc).replace(tzinfo=None)
    if end_time.tzinfo is not None:
        end_time = end_time.astimezone(tz.utc).replace(tzinfo=None)
    
    new_event = Event(
        title=event.title,
        description=event.description,
        location=event.location,
        start_time=start_time,
        end_time=end_time,
        share_slug=generate_share_slug(event.title),
        created_by=current_user.id  # Track who created the event
    )
    db.add(new_event)
    db.commit()
    db.refresh(new_event)
    
    # Audit log: Event created
    create_audit_log(
        db=db,
        event_id=new_event.id,
        user_id=current_user.id,
        action_type="event_created",
        details={
            "title": new_event.title,
            "location": new_event.location,
            "start_time": new_event.start_time.isoformat(),
            "end_time": new_event.end_time.isoformat()
        },
        ip_address=request.client.host if request.client else None
    )
    
    return new_event


@router.get("/", response_model=EventsPaginatedResponse)
def get_events(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_organizer)
):
    """Get events with pagination - Organizers see only their events, Admins see all"""
    # Build query based on user role
    query = db.query(Event)
    
    # Admins can see all events, Organizers only their own
    if current_user.role != "ADMIN":
        query = query.filter(Event.created_by == current_user.id)
    
    # Get total count
    total = query.count()
    
    # Apply pagination and order by created date desc
    events = query.order_by(Event.created_at.desc()).offset(skip).limit(limit).all()
    
    # Convert SQLAlchemy models to Pydantic schemas
    events_response = [EventResponse.model_validate(event) for event in events]
    
    return EventsPaginatedResponse(
        total=total,
        skip=skip,
        limit=limit,
        events=events_response
    )


@router.get("/{event_id}/share")
def get_share_link(event_id: int, db: Session = Depends(get_db)):
    from app.core.config import settings

    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    return {
        "share_url": f"{settings.FRONTEND_URL}/register/{event.share_slug}"
    }
    
    
@router.put("/{event_id}", response_model=EventResponse)
def update_event(
    event_id: int, 
    payload: EventCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_organizer)
):
    """Update event - Organizers can only update their own events, Admins can update any"""
    event = db.query(Event).filter(Event.id == event_id).first()

    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Check ownership: Organizers can only edit their own events
    if current_user.role == "ORGANIZER" and event.created_by != current_user.id:
        raise HTTPException(
            status_code=403, 
            detail="You can only edit your own events"
        )
    
    # Convert timezone-aware times to naive UTC for storage
    from datetime import timezone as tz
    start_time = payload.start_time
    end_time = payload.end_time
    
    if start_time.tzinfo is not None:
        start_time = start_time.astimezone(tz.utc).replace(tzinfo=None)
    if end_time.tzinfo is not None:
        end_time = end_time.astimezone(tz.utc).replace(tzinfo=None)
    
    # Track changes for audit log
    changes = {}
    if event.title != payload.title:
        changes["title"] = {"old": event.title, "new": payload.title}
    if event.description != payload.description:
        changes["description"] = {"old": event.description, "new": payload.description}
    if event.location != payload.location:
        changes["location"] = {"old": event.location, "new": payload.location}
    if event.start_time != start_time:
        changes["start_time"] = {"old": event.start_time.isoformat() if event.start_time else None, "new": start_time.isoformat()}
    if event.end_time != end_time:
        changes["end_time"] = {"old": event.end_time.isoformat() if event.end_time else None, "new": end_time.isoformat()}

    event.title = payload.title
    event.description = payload.description
    event.location = payload.location
    event.start_time = start_time
    event.end_time = end_time

    db.commit()
    db.refresh(event)
    
    # Audit log: Event edited (only if there were changes)
    if changes:
        create_audit_log(
            db=db,
            event_id=event.id,
            user_id=current_user.id,
            action_type="event_edited",
            details={"changes": changes},
            ip_address=request.client.host if request.client else None
        )

    return event

@router.delete("/{event_id}")
def delete_event(
    event_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_organizer)
):
    """Delete event - ADMIN ONLY"""
    # Only admins can delete events
    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=403,
            detail="Only administrators can delete events"
        )
    
    event = db.query(Event).filter(Event.id == event_id).first()

    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Audit log: Event deleted (log before deletion)
    create_audit_log(
        db=db,
        event_id=event.id,
        user_id=current_user.id,
        action_type="event_deleted",
        details={
            "title": event.title,
            "location": event.location
        },
        ip_address=request.client.host if request.client else None
    )

    db.delete(event)
    db.commit()

    return {"message": "Event deleted successfully"}


@router.get("/{event_id}/audit-logs", response_model=List[AuditLogResponse])
def get_audit_logs(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_organizer)
):
    """Get audit logs for an event - Organizers can only see logs for their events, Admins see all"""
    event = db.query(Event).filter(Event.id == event_id).first()
    
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Check permissions: Organizers can only see logs for their own events
    if current_user.role == "ORGANIZER" and event.created_by != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can only view audit logs for your own events"
        )
    
    logs = get_event_audit_logs(db, event_id)
    
    # Enrich logs with user email
    result = []
    for log in logs:
        log_dict = {
            "id": log.id,
            "event_id": log.event_id,
            "user_id": log.user_id,
            "user_email": log.user.email if log.user else "System",
            "action_type": log.action_type,
            "details": log.details,
            "ip_address": log.ip_address,
            "timestamp": log.timestamp
        }
        result.append(log_dict)
    
    return result


@router.get("/{event_id}/report")
def generate_event_report(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_organizer)
):
    """
    Generate PDF report for an event with attendance statistics
    Includes: Total registered, Total attended, Attendance %, Absentees list
    """
    # Get event to verify it exists and check permissions
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Check permissions: Organizers can only generate reports for their own events
    if current_user.role == "ORGANIZER" and event.created_by != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can only generate reports for your own events"
        )
    
    try:
        # Generate PDF
        pdf_buffer = generate_event_report_pdf(db, event_id)
        
        # Return as downloadable PDF
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=Event_Report_{event.share_slug}_{event_id}.pdf"
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        import traceback
        print(f"Error generating report: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {str(e)}")