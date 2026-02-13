"""
Anomaly Detection API Routes - Phase 2
======================================

Endpoints for ML-based anomaly detection in attendance patterns.
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta

from app.db.database import get_db
from app.services.anomaly_detection_service import AnomalyDetectionService
from app.security.jwt import get_current_user
from app.models.user import User
from app.models.attendance import Attendance
from app.core.permissions import require_admin, require_organizer


router = APIRouter(prefix="/analytics/anomaly", tags=["Analytics - Phase 2: Anomaly Detection"])

# Singleton instance of anomaly detection service
anomaly_service = AnomalyDetectionService()


@router.post("/train")
def train_anomaly_model(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Train the anomaly detection model on historical data
    
    **Permissions:** Admin only
    
    **Returns:**
    - Training statistics
    - Feature list
    - Model parameters
    - Anomaly rate in training data
    
    **Note:** Requires at least 10 attendance records for training
    """
    result = anomaly_service.train_anomaly_detector(db)
    
    if 'error' in result:
        raise HTTPException(status_code=400, detail=result)
    
    return {
        "status": "trained",
        "message": "Anomaly detection model trained successfully",
        **result
    }


@router.get("/detect")
def detect_anomalies(
    event_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_organizer)
):
    """
    Detect anomalies in attendance records
    
    **Permissions:** Organizer and above
    
    **Parameters:**
    - event_id (optional): Filter anomalies for specific event
    
    **Returns:**
    - List of detected anomalies
    - Anomaly scores and severity levels
    - Feature values and explanations
    - Overall statistics
    """
    result = anomaly_service.detect_anomalies(db, event_id)
    
    if 'error' in result:
        raise HTTPException(status_code=400, detail=result)
    
    return result


@router.get("/explain/{attendance_id}")
def explain_anomaly(
    attendance_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_organizer)
):
    """
    Get detailed explanation for specific attendance anomaly
    
    **Permissions:** Organizer and above
    
    **Parameters:**
    - attendance_id: ID of the attendance record to explain
    
    **Returns:**
    - Human-readable explanation
    - Feature values
    - Attendance record details
    """
    attendance = db.query(Attendance).filter(Attendance.id == attendance_id).first()
    if not attendance:
        raise HTTPException(status_code=404, detail="Attendance record not found")
    
    # Extract features for this single record
    df = anomaly_service.extract_features(db, [attendance])
    
    if df.empty:
        raise HTTPException(
            status_code=400,
            detail="Could not extract features for this attendance record"
        )
    
    features = df.iloc[0].drop('attendance_id').to_dict()
    explanation = anomaly_service.explain_anomaly(features)
    
    return {
        'attendance_id': attendance_id,
        'student_prn': attendance.student_prn,
        'event_id': attendance.event_id,
        'scanned_at': attendance.scanned_at.isoformat(),
        'scan_source': attendance.scan_source,
        'explanation': explanation,
        'features': features
    }


@router.get("/summary")
def get_anomaly_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_organizer)
):
    """
    Get overall anomaly detection statistics
    
    **Permissions:** Organizer and above
    
    **Returns:**
    - Total anomalies detected
    - Breakdown by severity (HIGH/MEDIUM)
    - Breakdown by scan source
    - Count requiring immediate review
    """
    result = anomaly_service.get_anomaly_summary(db)
    
    if 'error' in result:
        raise HTTPException(status_code=400, detail=result)
    
    return result


@router.get("/status")
def get_model_status(
    current_user: User = Depends(get_current_user)
):
    """
    Check if anomaly detection model is trained and ready
    
    **Permissions:** Any authenticated user
    
    **Returns:**
    - Training status
    - Model configuration
    - Training metadata
    - Feature importance
    """
    base_status = {
        'is_trained': anomaly_service.is_trained,
        'model_type': 'Isolation Forest',
        'contamination_rate': anomaly_service.model.contamination,
        'n_estimators': anomaly_service.model.n_estimators,
        'status': 'ready' if anomaly_service.is_trained else 'requires_training',
        'message': 'Model is trained and ready for anomaly detection' if anomaly_service.is_trained 
                   else 'Model needs training. Admin must run /train endpoint first.'
    }
    
    # Add training metadata if available
    if anomaly_service.is_trained and anomaly_service.training_metadata:
        base_status.update({
            'training_info': anomaly_service.training_metadata,
            'model_health': 'EXCELLENT' if anomaly_service.training_metadata.get('samples_used', 0) > 100
                           else 'GOOD' if anomaly_service.training_metadata.get('samples_used', 0) > 50
                           else 'FAIR'
        })
    
    return base_status


@router.get("/metrics")
def get_model_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_organizer)
):
    """
    Get detailed model performance metrics and analytics
    
    **Permissions:** Organizer and above
    
    **Returns:**
    - Feature importance rankings
    - Model performance statistics
    - Detection distribution
    - Confidence metrics
    """
    if not anomaly_service.is_trained:
        raise HTTPException(
            status_code=400,
            detail="Model not trained yet. Train the model first."
        )
    
    # Get current detection results
    result = anomaly_service.detect_anomalies(db)
    
    if 'error' in result:
        raise HTTPException(status_code=400, detail=result)
    
    # Calculate distribution metrics
    anomalies = result.get('anomalies', [])
    scores = [a['anomaly_score'] for a in anomalies]
    
    severity_dist = {
        'HIGH': len([a for a in anomalies if a['severity'] == 'HIGH']),
        'MEDIUM': len([a for a in anomalies if a['severity'] == 'MEDIUM'])
    }
    
    from datetime import timedelta
    now = datetime.now()
    time_buckets = {}
    for i in range(7):
        date = (now - timedelta(days=i)).strftime('%Y-%m-%d')
        time_buckets[date] = 0
    
    for anomaly in anomalies:
        try:
            anomaly_date = datetime.fromisoformat(anomaly['scanned_at']).strftime('%Y-%m-%d')
            if anomaly_date in time_buckets:
                time_buckets[anomaly_date] += 1
        except:
            pass
    
    return {
        'model_metadata': anomaly_service.training_metadata,
        'current_detections': {
            'total': len(anomalies),
            'by_severity': severity_dist,
            'avg_score': round(sum(scores) / len(scores), 3) if scores else 0,
            'min_score': round(min(scores), 3) if scores else 0,
            'max_score': round(max(scores), 3) if scores else 0
        },
        'feature_importance': anomaly_service.training_metadata.get('feature_importance', {}),
        'time_distribution': dict(sorted(time_buckets.items())),
        'model_confidence': anomaly_service.training_metadata.get('confidence', 'UNKNOWN'),
        'last_trained': anomaly_service.training_metadata.get('trained_at', 'Unknown')
    }

