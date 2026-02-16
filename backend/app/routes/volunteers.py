"""
Volunteer Management Routes
Allows organizers to add volunteers to events and manage volunteer certificates
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import List

from app.db.database import get_db
from app.models.user import User, UserRole
from app.models.event import Event
from app.models.volunteer import Volunteer
from app.models.certificate import Certificate
from app.core.permissions import require_organizer
from app.services.audit_service import create_audit_log

router = APIRouter(prefix="/volunteers", tags=["Volunteers"])


class VolunteerCreate(BaseModel):
    """Request body for adding a volunteer"""
    name: str
    email: EmailStr


class VolunteerResponse(BaseModel):
    """Volunteer data response"""
    id: int
    event_id: int
    name: str
    email: str
    added_at: str
    certificate_sent: bool
    certificate_sent_at: str | None


@router.post("/{event_id}")
def add_volunteer(
    event_id: int,
    volunteer_data: VolunteerCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_organizer)
):
    """
    Add a volunteer to an event
    Only admins and event organizers can add volunteers
    """
    # Check if event exists
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Check permissions (must be admin or event creator)
    if current_user.role != UserRole.ADMIN and event.created_by != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Only event organizers and admins can add volunteers"
        )
    
    # Check if volunteer already exists for this event
    existing = db.query(Volunteer).filter(
        Volunteer.event_id == event_id,
        Volunteer.email == volunteer_data.email
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Volunteer with email {volunteer_data.email} already added to this event"
        )
    
    # Create volunteer record
    volunteer = Volunteer(
        event_id=event_id,
        name=volunteer_data.name,
        email=volunteer_data.email,
        added_by=current_user.id
    )
    
    db.add(volunteer)
    db.commit()
    db.refresh(volunteer)
    
    # Create audit log
    create_audit_log(
        db=db,
        event_id=event_id,
        user_id=current_user.id,
        action_type="volunteer_added",
        details={
            "volunteer_id": volunteer.id,
            "volunteer_name": volunteer.name,
            "volunteer_email": volunteer.email
        },
        ip_address=request.client.host if request.client else None
    )
    
    return {
        "success": True,
        "message": f"Volunteer {volunteer.name} added successfully",
        "volunteer": {
            "id": volunteer.id,
            "name": volunteer.name,
            "email": volunteer.email,
            "added_at": volunteer.added_at.isoformat()
        }
    }


@router.get("/{event_id}")
def list_volunteers(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_organizer)
):
    """
    Get all volunteers for an event
    """
    # Check if event exists
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Check permissions
    if current_user.role != UserRole.ADMIN and event.created_by != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Only event organizers and admins can view volunteers"
        )
    
    volunteers = db.query(Volunteer).filter(Volunteer.event_id == event_id).all()
    
    return {
        "event_id": event_id,
        "event_title": event.title,
        "total_volunteers": len(volunteers),
        "volunteers": [
            {
                "id": v.id,
                "name": v.name,
                "email": v.email,
                "added_at": v.added_at.isoformat(),
                "certificate_sent": v.certificate_sent,
                "certificate_sent_at": v.certificate_sent_at.isoformat() if v.certificate_sent_at else None
            }
            for v in volunteers
        ]
    }


@router.delete("/{volunteer_id}")
def remove_volunteer(
    volunteer_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_organizer)
):
    """
    Remove a volunteer from an event
    Only admins and event organizers can remove volunteers
    """
    volunteer = db.query(Volunteer).filter(Volunteer.id == volunteer_id).first()
    if not volunteer:
        raise HTTPException(status_code=404, detail="Volunteer not found")
    
    # Check if event exists and user has permission
    event = db.query(Event).filter(Event.id == volunteer.event_id).first()
    if current_user.role != UserRole.ADMIN and event.created_by != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Only event organizers and admins can remove volunteers"
        )
    
    # Store info for audit log before deleting
    volunteer_name = volunteer.name
    volunteer_email = volunteer.email
    event_id = volunteer.event_id
    
    db.delete(volunteer)
    db.commit()
    
    # Create audit log
    create_audit_log(
        db=db,
        event_id=event_id,
        user_id=current_user.id,
        action_type="volunteer_removed",
        details={
            "volunteer_id": volunteer_id,
            "volunteer_name": volunteer_name,
            "volunteer_email": volunteer_email
        },
        ip_address=request.client.host if request.client else None
    )
    
    return {
        "success": True,
        "message": f"Volunteer {volunteer_name} removed successfully"
    }


@router.post("/{volunteer_id}/resend-certificate")
def resend_volunteer_certificate(
    volunteer_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_organizer)
):
    """
    Resend certificate to a volunteer
    Useful if email failed or volunteer lost the certificate
    """
    volunteer = db.query(Volunteer).filter(Volunteer.id == volunteer_id).first()
    if not volunteer:
        raise HTTPException(status_code=404, detail="Volunteer not found")
    
    # Check permissions
    event = db.query(Event).filter(Event.id == volunteer.event_id).first()
    if current_user.role != UserRole.ADMIN and event.created_by != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Only event organizers and admins can resend certificates"
        )
    
    # Find volunteer's certificate
    certificate = db.query(Certificate).filter(
        Certificate.event_id == volunteer.event_id,
        Certificate.recipient_email == volunteer.email,
        Certificate.role_type == "volunteer"
    ).first()
    
    if not certificate:
        raise HTTPException(
            status_code=404,
            detail="No certificate found for this volunteer. Push certificates first."
        )
    
    try:
        # Import certificate service to resend email
        from app.services.certificate_service import send_certificate_email
        
        success = send_certificate_email(
            db=db,
            certificate_id=certificate.certificate_id,
            recipient_email=volunteer.email,
            recipient_name=volunteer.name,
            event_title=event.title
        )
        
        if success:
            # Update volunteer record
            from datetime import datetime, timezone
            volunteer.certificate_sent = True
            volunteer.certificate_sent_at = datetime.now(timezone.utc)
            
            # Update certificate record
            certificate.email_sent = True
            certificate.email_sent_at = datetime.now(timezone.utc)
            
            db.commit()
            
            # Create audit log
            create_audit_log(
                db=db,
                event_id=volunteer.event_id,
                user_id=current_user.id,
                action_type="volunteer_certificate_resent",
                details={
                    "volunteer_id": volunteer.id,
                    "volunteer_name": volunteer.name,
                    "volunteer_email": volunteer.email,
                    "certificate_id": certificate.certificate_id
                },
                ip_address=request.client.host if request.client else None
            )
            
            return {
                "success": True,
                "message": f"Certificate resent to {volunteer.email}"
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to send certificate email. Check SMTP configuration."
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to resend certificate: {str(e)}"
        )
