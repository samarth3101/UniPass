from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from app.db.database import get_db
from app.models.user import User, UserRole
from app.models.event import Event
from app.models.attendance import Attendance
from app.core.permissions import require_admin

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/organizers")
def get_all_organizers(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Admin-only: Get all organizers with their event statistics
    """
    organizers = db.query(User).filter(User.role == UserRole.ORGANIZER).all()
    
    result = []
    for organizer in organizers:
        # Count events created by this organizer
        event_count = db.query(func.count(Event.id)).filter(
            Event.created_by == organizer.id
        ).scalar()
        
        # Get total registrations across all their events (count tickets)
        from app.models.ticket import Ticket
        total_registrations = db.query(func.count(Ticket.id)).join(
            Event, Ticket.event_id == Event.id
        ).filter(
            Event.created_by == organizer.id
        ).scalar()
        
        # Get total attended (count attendance records)
        total_attended = db.query(func.count(Attendance.id)).join(
            Event, Attendance.event_id == Event.id
        ).filter(
            Event.created_by == organizer.id
        ).scalar()
        
        result.append({
            "id": organizer.id,
            "email": organizer.email,
            "full_name": organizer.full_name,
            "created_at": organizer.created_at if hasattr(organizer, 'created_at') else None,
            "event_count": event_count or 0,
            "total_registrations": total_registrations or 0,
            "total_attended": total_attended or 0,
        })
    
    return result


@router.get("/scanners")
def get_all_scanners(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Admin-only: Get all scanner operators
    """
    scanners = db.query(User).filter(User.role == UserRole.SCANNER).all()
    
    result = []
    for scanner in scanners:
        result.append({
            "id": scanner.id,
            "email": scanner.email,
            "role": scanner.role.value,
        })
    
    return result


@router.get("/admins")
def get_all_admins(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Admin-only: Get all admin users
    """
    admins = db.query(User).filter(User.role == UserRole.ADMIN).all()
    
    result = []
    for admin in admins:
        result.append({
            "id": admin.id,
            "email": admin.email,
            "full_name": admin.full_name,
            "created_at": admin.created_at,
        })
    
    return result
