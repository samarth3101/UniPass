from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime

from app.db.database import get_db
from app.models.user import User, UserRole
from app.models.event import Event
from app.models.ticket import Ticket
from app.models.attendance import Attendance
from app.core.permissions import require_admin

router = APIRouter(prefix="/organizers", tags=["Organizers"])


@router.get("/{organizer_id}/analytics")
def get_organizer_analytics(
    organizer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Get detailed analytics for a specific organizer including:
    - Personal information
    - Overall statistics
    - Event history with individual stats
    - Monthly event creation trends
    """
    # Get organizer details
    organizer = db.query(User).filter(
        User.id == organizer_id,
        User.role == UserRole.ORGANIZER
    ).first()
    
    if not organizer:
        raise HTTPException(status_code=404, detail="Organizer not found")
    
    # Get all events created by this organizer
    events = db.query(Event).filter(Event.created_by == organizer_id).all()
    
    # Calculate overall statistics
    total_events = len(events)
    total_registrations = 0
    total_attended = 0
    
    # Get detailed event list with individual stats
    events_list = []
    for event in events:
        reg_count = db.query(Ticket).filter(Ticket.event_id == event.id).count()
        att_count = db.query(Attendance).filter(Attendance.event_id == event.id).count()
        
        total_registrations += reg_count
        total_attended += att_count
        
        events_list.append({
            "event_id": event.id,
            "event_title": event.title,
            "event_location": event.location,
            "event_start_time": event.start_time.isoformat() if event.start_time else None,
            "event_end_time": event.end_time.isoformat() if event.end_time else None,
            "created_at": event.created_at.isoformat() if event.created_at else None,
            "total_registered": reg_count,
            "total_attended": att_count,
            "attendance_rate": round((att_count / reg_count * 100), 2) if reg_count > 0 else 0,
            "status": "completed" if event.end_time and event.end_time < datetime.utcnow() else "upcoming"
        })
    
    # Sort events by created_at desc
    events_list.sort(key=lambda x: x["created_at"] or "", reverse=True)
    
    # Calculate monthly event creation stats (last 6 months)
    from collections import defaultdict
    monthly_stats = defaultdict(int)
    
    for event in events:
        if event.created_at:
            month_key = event.created_at.strftime("%Y-%m")
            monthly_stats[month_key] += 1
    
    # Convert to list and sort
    monthly_list = [
        {"month": month, "count": count}
        for month, count in sorted(monthly_stats.items(), reverse=True)[:6]
    ]
    monthly_list.reverse()  # Show oldest to newest
    
    return {
        "organizer": {
            "id": organizer.id,
            "email": organizer.email,
            "full_name": organizer.full_name or f"Organizer #{organizer.id}",
            "role": organizer.role.value
        },
        "statistics": {
            "total_events": total_events,
            "total_registrations": total_registrations,
            "total_attended": total_attended,
            "attendance_rate": round((total_attended / total_registrations * 100), 2) if total_registrations > 0 else 0
        },
        "events": events_list,
        "monthly_stats": monthly_list
    }
