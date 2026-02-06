from fastapi import APIRouter, Depends, HTTPException
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
    Admin-only: Get all scanner operators with scan statistics
    """
    scanners = db.query(User).filter(User.role == UserRole.SCANNER).all()
    
    result = []
    for scanner in scanners:
        # Count total scans performed by this scanner
        # Attendance records are created when scanners scan tickets
        scan_count = db.query(func.count(Attendance.id)).filter(
            Attendance.id.in_(
                db.query(Attendance.id).filter(
                    # We need to track who scanned - for now use all attendance
                    Attendance.id > 0
                )
            )
        ).scalar() or 0
        
        result.append({
            "id": scanner.id,
            "email": scanner.email,
            "full_name": scanner.full_name,
            "role": scanner.role.value,
            "total_scans": scan_count,  # Will be properly implemented when scanner_id tracking is added
            "created_at": scanner.created_at if hasattr(scanner, 'created_at') else None,
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


@router.get("/scanners/{scanner_id}/analytics")
def get_scanner_analytics(
    scanner_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Get detailed analytics for a specific scanner including:
    - Personal information
    - Scan statistics
    - Recent scans with student details
    """
    # Get scanner details
    scanner = db.query(User).filter(
        User.id == scanner_id,
        User.role == UserRole.SCANNER
    ).first()
    
    if not scanner:
        raise HTTPException(status_code=404, detail="Scanner not found")
    
    # Get all attendance records (representing scans)
    # Note: In a production system, you'd track scanner_id in Attendance table
    # For now, we'll show recent scans across all events
    recent_scans = db.query(Attendance).order_by(
        Attendance.scanned_at.desc()
    ).limit(50).all()
    
    # Build scan list with student and event details
    scans_list = []
    unique_students = set()
    unique_events = set()
    
    for scan in recent_scans:
        from app.models.student import Student
        student = db.query(Student).filter(Student.prn == scan.student_prn).first()
        event = db.query(Event).filter(Event.id == scan.event_id).first()
        
        unique_students.add(scan.student_prn)
        unique_events.add(scan.event_id)
        
        scans_list.append({
            "attendance_id": scan.id,
            "student_prn": scan.student_prn,
            "student_name": student.name if student else "Unknown",
            "student_email": student.email if student else None,
            "student_branch": student.branch if student else None,
            "event_id": scan.event_id,
            "event_title": event.title if event else "Unknown Event",
            "scanned_at": scan.scanned_at.isoformat() if scan.scanned_at else None
        })
    
    return {
        "scanner": {
            "id": scanner.id,
            "email": scanner.email,
            "full_name": scanner.full_name or f"Scanner #{scanner.id}",
            "role": scanner.role.value
        },
        "statistics": {
            "total_scans": len(scans_list),
            "unique_students": len(unique_students),
            "unique_events": len(unique_events)
        },
        "recent_scans": scans_list
    }


@router.put("/users/{user_id}/name")
def update_user_name(
    user_id: int,
    full_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Admin-only: Update user's display name
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not full_name or not full_name.strip():
        raise HTTPException(status_code=400, detail="Name cannot be empty")
    
    user.full_name = full_name.strip()
    db.commit()
    db.refresh(user)
    
    return {
        "success": True,
        "message": "Name updated successfully",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role.value
        }
    }


@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Admin-only: Delete a user (scanner or organizer)
    Prevents deletion of admin users for safety
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Prevent deleting admin users
    if user.role == UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Cannot delete admin users")
    
    # Prevent users from deleting themselves
    if user.id == current_user.id:
        raise HTTPException(status_code=403, detail="Cannot delete your own account")
    
    # Check if organizer has created events
    if user.role == UserRole.ORGANIZER:
        event_count = db.query(func.count(Event.id)).filter(
            Event.created_by == user.id
        ).scalar()
        
        if event_count and event_count > 0:
            raise HTTPException(
                status_code=400, 
                detail=f"Cannot delete organizer with {event_count} existing event(s). Please delete or reassign their events first."
            )
    
    # Store user info for response
    user_info = {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role.value
    }
    
    # Delete the user
    db.delete(user)
    db.commit()
    
    return {
        "success": True,
        "message": f"{user.role.value.capitalize()} deleted successfully",
        "deleted_user": user_info
    }
