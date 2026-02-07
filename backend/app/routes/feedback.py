from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

from app.db.database import get_db
from app.models.feedback import Feedback
from app.models.event import Event
from app.models.attendance import Attendance
from app.models.student import Student
from app.models.user import User
from app.schemas.feedback import (
    FeedbackCreate, 
    FeedbackResponse, 
    FeedbackSummary,
    SendFeedbackRequest
)
from app.core.permissions import require_organizer
from app.services.email_service import send_feedback_request_email
from app.services.audit_service import create_audit_log

router = APIRouter(prefix="/feedback", tags=["Feedback"])


@router.post("/send-requests/{event_id}")
def send_feedback_requests(
    event_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_organizer)
):
    """
    Send feedback form links to all students who attended the event.
    Only sends to students who actually scanned (not just registered).
    """
    # Verify event exists and user has access
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Check ownership (organizers can only send for their events, admins for all)
    if current_user.role != "ADMIN" and event.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="You can only send feedback for your own events")
    
    # Get all students who actually attended (not just registered)
    attended_students = db.query(Attendance).filter(
        Attendance.event_id == event_id
    ).all()
    
    if not attended_students:
        raise HTTPException(status_code=400, detail="No students attended this event")
    
    # Send emails to attended students
    sent_count = 0
    failed_count = 0
    
    for attendance in attended_students:
        student = db.query(Student).filter(Student.prn == attendance.student_prn).first()
        
        if student and student.email:
            try:
                # Check if already submitted feedback
                existing_feedback = db.query(Feedback).filter(
                    Feedback.event_id == event_id,
                    Feedback.student_prn == student.prn
                ).first()
                
                if existing_feedback:
                    continue  # Skip if already submitted
                
                send_feedback_request_email(
                    to_email=student.email,
                    student_name=student.name,
                    event_title=event.title,
                    event_id=event.id,
                    student_prn=student.prn
                )
                sent_count += 1
            except Exception as e:
                failed_count += 1
                print(f"Failed to send feedback email to {student.email}: {str(e)}")
    
    # Audit log
    create_audit_log(
        db=db,
        event_id=event_id,
        user_id=current_user.id,
        action_type="feedback_requests_sent",
        details={
            "sent_count": sent_count,
            "failed_count": failed_count,
            "total_attended": len(attended_students)
        },
        ip_address=request.client.host if request.client else None
    )
    
    return {
        "status": "success",
        "total_attended": len(attended_students),
        "emails_sent": sent_count,
        "emails_failed": failed_count,
        "already_submitted": len(attended_students) - sent_count - failed_count
    }


@router.post("/submit", response_model=FeedbackResponse)
def submit_feedback(
    feedback: FeedbackCreate,
    db: Session = Depends(get_db)
):
    """
    Public endpoint for students to submit feedback.
    Validates that student actually attended the event.
    """
    # Verify event exists
    event = db.query(Event).filter(Event.id == feedback.event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Verify student attended the event (not just registered)
    attendance = db.query(Attendance).filter(
        Attendance.event_id == feedback.event_id,
        Attendance.student_prn == feedback.student_prn
    ).first()
    
    if not attendance:
        raise HTTPException(
            status_code=403, 
            detail="You cannot submit feedback. You must have attended the event."
        )
    
    # Check if feedback already submitted
    existing_feedback = db.query(Feedback).filter(
        Feedback.event_id == feedback.event_id,
        Feedback.student_prn == feedback.student_prn
    ).first()
    
    if existing_feedback:
        raise HTTPException(
            status_code=409, 
            detail="You have already submitted feedback for this event"
        )
    
    # Create feedback record
    new_feedback = Feedback(
        event_id=feedback.event_id,
        student_prn=feedback.student_prn,
        overall_rating=feedback.overall_rating,
        content_quality=feedback.content_quality,
        organization_rating=feedback.organization_rating,
        venue_rating=feedback.venue_rating,
        speaker_rating=feedback.speaker_rating,
        what_liked=feedback.what_liked,
        what_improve=feedback.what_improve,
        additional_comments=feedback.additional_comments,
        would_recommend=feedback.would_recommend
    )
    
    # Basic sentiment analysis (simple rule-based for now)
    # AI service can enhance this later
    avg_rating = (
        feedback.overall_rating + 
        feedback.content_quality + 
        feedback.organization_rating + 
        feedback.venue_rating
    ) / 4
    
    if avg_rating >= 4:
        new_feedback.sentiment_score = 1  # Positive
    elif avg_rating >= 3:
        new_feedback.sentiment_score = 0  # Neutral
    else:
        new_feedback.sentiment_score = -1  # Negative
    
    db.add(new_feedback)
    db.commit()
    db.refresh(new_feedback)
    
    return new_feedback


@router.get("/event/{event_id}/summary", response_model=FeedbackSummary)
def get_feedback_summary(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_organizer)
):
    """
    Get aggregated feedback summary for an event.
    Organizers can only view their own events, admins can view all.
    """
    # Verify event exists
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Check ownership
    if current_user.role != "ADMIN" and event.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get all feedback for event
    feedbacks = db.query(Feedback).filter(Feedback.event_id == event_id).all()
    
    if not feedbacks:
        raise HTTPException(status_code=404, detail="No feedback submitted yet")
    
    total = len(feedbacks)
    
    # Calculate averages
    avg_overall = sum(f.overall_rating for f in feedbacks) / total
    avg_content = sum(f.content_quality for f in feedbacks) / total
    avg_organization = sum(f.organization_rating for f in feedbacks) / total
    avg_venue = sum(f.venue_rating for f in feedbacks) / total
    
    # Speaker rating (may be None for some)
    speaker_ratings = [f.speaker_rating for f in feedbacks if f.speaker_rating]
    avg_speaker = sum(speaker_ratings) / len(speaker_ratings) if speaker_ratings else None
    
    # Recommendation percentage
    recommend_count = sum(1 for f in feedbacks if f.would_recommend)
    recommend_percentage = (recommend_count / total) * 100
    
    # Sentiment breakdown
    sentiment_breakdown = {
        "positive": sum(1 for f in feedbacks if f.sentiment_score == 1),
        "neutral": sum(1 for f in feedbacks if f.sentiment_score == 0),
        "negative": sum(1 for f in feedbacks if f.sentiment_score == -1)
    }
    
    return FeedbackSummary(
        event_id=event_id,
        total_responses=total,
        average_overall=round(avg_overall, 2),
        average_content=round(avg_content, 2),
        average_organization=round(avg_organization, 2),
        average_venue=round(avg_venue, 2),
        average_speaker=round(avg_speaker, 2) if avg_speaker else None,
        recommend_percentage=round(recommend_percentage, 1),
        sentiment_breakdown=sentiment_breakdown
    )


@router.get("/event/{event_id}", response_model=List[FeedbackResponse])
def get_event_feedback(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_organizer)
):
    """
    Get all feedback submissions for an event.
    """
    # Verify event exists
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Check ownership
    if current_user.role != "ADMIN" and event.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    feedbacks = db.query(Feedback).filter(
        Feedback.event_id == event_id
    ).order_by(Feedback.submitted_at.desc()).all()
    
    return feedbacks


@router.get("/check-eligibility/{event_id}/{student_prn}")
def check_feedback_eligibility(
    event_id: int,
    student_prn: str,
    db: Session = Depends(get_db)
):
    """
    Check if a student is eligible to submit feedback (attended and hasn't submitted yet).
    Public endpoint for feedback form validation.
    """
    # Check if attended
    attendance = db.query(Attendance).filter(
        Attendance.event_id == event_id,
        Attendance.student_prn == student_prn
    ).first()
    
    if not attendance:
        return {
            "eligible": False,
            "reason": "You did not attend this event"
        }
    
    # Check if already submitted
    existing_feedback = db.query(Feedback).filter(
        Feedback.event_id == event_id,
        Feedback.student_prn == student_prn
    ).first()
    
    if existing_feedback:
        return {
            "eligible": False,
            "reason": "You have already submitted feedback for this event"
        }
    
    return {
        "eligible": True,
        "reason": None
    }
