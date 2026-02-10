"""
Analytics API Routes - Phase 1: Descriptive Analytics
Provides statistical insights from attendance data without ML
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
from app.db.database import get_db
from app.services.analytics_service import DescriptiveAnalyticsService
from app.security.jwt import get_current_user
from app.models.user import User

router = APIRouter(prefix="/analytics/descriptive", tags=["Analytics - Phase 1"])


@router.get("/event/{event_id}/distribution")
def get_event_distribution(
    event_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get attendance distribution for specific event
    
    Returns:
    - Total attendance and capacity
    - Temporal distribution (early, on-time, late)
    - Scan window duration
    - Peak scan time
    """
    service = DescriptiveAnalyticsService(db)
    result = service.get_event_attendance_distribution(event_id)
    
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return result


@router.get("/student/{prn}/consistency")
def get_student_consistency(
    prn: str, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get individual student attendance patterns
    
    Returns:
    - Total attendance count and rate
    - Attendance by event type
    - Punctuality metrics (late arrival analysis)
    """
    service = DescriptiveAnalyticsService(db)
    return service.get_student_attendance_consistency(prn)


@router.get("/departments/participation")
def get_department_stats(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get department-wise participation statistics
    
    Returns:
    - Active students per department
    - Participation rates
    - Average events per student by department
    """
    service = DescriptiveAnalyticsService(db)
    
    # Parse date strings if provided
    start = datetime.fromisoformat(start_date) if start_date else None
    end = datetime.fromisoformat(end_date) if end_date else None
    
    return service.get_department_participation(start, end)


@router.get("/time-patterns")
def get_time_patterns(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Analyze best times for events based on historical attendance
    
    Returns:
    - Average attendance by hour of day
    - Average attendance by day of week
    - Best time recommendations (hour and day)
    """
    service = DescriptiveAnalyticsService(db)
    
    # Parse date strings if provided
    start = datetime.fromisoformat(start_date) if start_date else None
    end = datetime.fromisoformat(end_date) if end_date else None
    
    return service.get_time_pattern_analysis(start, end)


@router.get("/summary")
def get_summary(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get overall system statistics summary
    
    Returns:
    - Total events, students, attendance records
    - Student engagement rate
    - Average attendance per event
    - Date range of events
    """
    service = DescriptiveAnalyticsService(db)
    
    # Parse date strings if provided
    start = datetime.fromisoformat(start_date) if start_date else None
    end = datetime.fromisoformat(end_date) if end_date else None
    
    return service.get_overall_summary(start, end)
