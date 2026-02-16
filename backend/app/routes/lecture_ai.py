"""
Cortex Lecture Intelligence Engine - API Routes
Endpoints for audio upload and report retrieval
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
import json

from app.db.database import get_db
from app.models.user import User
from app.models.event import Event
from app.models.lecture_report import LectureReport
from app.core.permissions import require_organizer, get_current_user
from app.services.lecture_ai_service import LectureAIService
from app.services.audit_service import create_audit_log

router = APIRouter(prefix="/ai/lecture", tags=["Cortex Lecture AI"])


@router.post("/upload/{event_id}")
async def upload_lecture_audio(
    event_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_organizer)
):
    """
    Upload audio recording for an event and trigger AI processing
    
    Requirements:
    - User must be admin or event organizer
    - Allowed formats: mp3, wav, m4a
    - Max file size: 100MB
    
    Returns:
    - Report ID
    - Processing status
    """
    # Verify event exists
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Check permissions
    if current_user.role != "ADMIN" and event.created_by != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Only event organizer or admin can upload lecture audio"
        )
    
    # Process audio through AI pipeline
    service = LectureAIService(db)
    try:
        report = await service.process_lecture_audio(
            event_id=event_id,
            user_id=current_user.id,
            file=file
        )
        
        # Log action
        create_audit_log(
            db=db,
            event_id=event_id,
            user_id=current_user.id,
            action_type="lecture_ai_upload",
            details={"filename": file.filename}
        )
        
        return {
            "report_id": report.id,
            "event_id": event_id,
            "status": report.status,
            "message": "Audio uploaded and processing initiated" if report.status == "completed" 
                      else "Audio processing in progress",
            "filename": report.audio_filename
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process audio: {str(e)}"
        )


@router.get("/report/{event_id}")
def get_lecture_report(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve AI-generated lecture report for an event
    
    Returns:
    - Full transcript
    - Extracted keywords
    - Structured AI summary
    - Metadata
    """
    # Verify event exists
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Check permissions
    if current_user.role not in ["ADMIN", "ORGANIZER"]:
        raise HTTPException(
            status_code=403,
            detail="Only admins and organizers can view lecture reports"
        )
    
    if current_user.role == "ORGANIZER" and event.created_by != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can only view reports for your own events"
        )
    
    # Get report
    service = LectureAIService(db)
    report = service.get_lecture_report(event_id)
    
    if not report:
        raise HTTPException(
            status_code=404,
            detail="No lecture report found for this event"
        )
    
    # Parse summary JSON
    summary_data = None
    if report.summary:
        try:
            summary_data = json.loads(report.summary)
        except:
            summary_data = {"raw_summary": report.summary}
    
    return {
        "report_id": report.id,
        "event": {
            "id": event.id,
            "title": event.title,
            "description": event.description,
            "start_time": event.start_time,
        },
        "status": report.status,
        "error_message": report.error_message,
        "transcript": report.transcript,
        "keywords": report.keywords,
        "summary": summary_data,
        "audio_filename": report.audio_filename,
        "generated_at": report.generated_at,
        "generated_by": {
            "id": report.creator.id,
            "email": report.creator.email,
            "full_name": report.creator.full_name
        }
    }


@router.get("/reports/all")
def get_all_lecture_reports(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_organizer)
):
    """
    Get all lecture reports (admin/organizer view)
    
    For organizers: only their events
    For admins: all events
    """
    service = LectureAIService(db)
    
    if current_user.role == "ADMIN":
        reports = service.get_all_reports(limit=limit)
    else:
        # Organizers see only their events
        reports = db.query(LectureReport).join(Event).filter(
            Event.created_by == current_user.id
        ).order_by(LectureReport.generated_at.desc()).limit(limit).all()
    
    return {
        "total": len(reports),
        "reports": [
            {
                "report_id": r.id,
                "event_id": r.event_id,
                "event_title": r.event.title,
                "status": r.status,
                "generated_at": r.generated_at,
                "keywords_count": len(r.keywords) if r.keywords else 0,
                "has_transcript": bool(r.transcript),
            }
            for r in reports
        ]
    }


@router.delete("/report/{report_id}")
def delete_lecture_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_organizer)
):
    """
    Delete a lecture report
    Only admin or event organizer can delete
    """
    report = db.query(LectureReport).filter(LectureReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # Check permissions
    event = db.query(Event).filter(Event.id == report.event_id).first()
    if current_user.role != "ADMIN" and event.created_by != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Only event organizer or admin can delete reports"
        )
    
    # Log action
    create_audit_log(
        db=db,
        event_id=report.event_id,
        user_id=current_user.id,
        action_type="lecture_ai_delete",
        details={"report_id": report_id}
    )
    
    db.delete(report)
    db.commit()
    
    return {"message": "Report deleted successfully"}
