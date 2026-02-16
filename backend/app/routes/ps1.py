"""
PS1 API Routes - Unified Campus Participation Intelligence System
Implements Features 1, 3, 4, 5 from PS1
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, timezone

from app.db.database import get_db
from app.security.jwt import get_current_user
from app.models.user import User, UserRole
from app.models.participation_role import ParticipationRole, RoleType
from app.models.certificate import Certificate
from app.services.reconciliation_service import ReconciliationService
from app.services.transcript_service import TranscriptService
from app.services.snapshot_service import SnapshotService
from app.services.audit_service import AuditService
from app.services.fraud_detection_service import FraudDetectionService
from app.services.qr_service import generate_certificate_qr_code, generate_transcript_qr_code
from app.models.attendance import Attendance

router = APIRouter(prefix="/ps1", tags=["PS1 - Participation Intelligence"])


# ============================================================================
# SCHEMAS
# ============================================================================

class ParticipationStatusResponse(BaseModel):
    canonical_status: str
    has_registration: bool
    has_attendance: bool
    has_certificate: bool
    attendance_count: int
    days_attended: int
    total_days_required: int
    certificate_revoked: bool
    conflicts: List[dict]
    trust_score: int
    raw_evidence: dict


class ConflictResponse(BaseModel):
    student_prn: str
    canonical_status: str
    conflicts: List[dict]
    trust_score: int


class RoleAssignmentRequest(BaseModel):
    student_prn: str
    role: str
    time_segment: Optional[str] = None


class RoleResponse(BaseModel):
    id: int
    event_id: int
    student_prn: str
    role: str
    assigned_at: datetime
    time_segment: Optional[str]


class CertificateVerificationResponse(BaseModel):
    authentic: bool
    certificate_id: Optional[str]
    student_prn: Optional[str]
    student_name: Optional[str]
    event_title: Optional[str]
    event_date: Optional[datetime]
    issued_at: Optional[datetime]
    revoked: bool
    revocation_reason: Optional[str]
    verification_hash_valid: bool
    message: str


class RevokeCertificateRequest(BaseModel):
    reason: str


class InvalidateAttendanceRequest(BaseModel):
    reason: str


class CorrectionRequest(BaseModel):
    correction_type: str  # "attendance", "certificate", "registration"
    old_value: str
    new_value: str
    reason: str


class BulkResolutionAction(BaseModel):
    """Action to take for a specific student's conflict"""
    student_prn: str
    action: str  # "add_attendance", "revoke_certificate", "ignore", "manual_review"
    reason: Optional[str] = None


class BulkResolutionRequest(BaseModel):
    """Bulk conflict resolution request"""
    actions: List[BulkResolutionAction]


class BulkResolutionResponse(BaseModel):
    """Response for bulk conflict resolution"""
    total_actions: int
    successful: int
    failed: int
    details: List[dict]


# ============================================================================
# FEATURE 1: PARTICIPATION RECONCILIATION
# ============================================================================

@router.get(
    "/participation/status/{event_id}/{student_prn}",
    response_model=ParticipationStatusResponse,
    summary="Get Canonical Participation Status",
    description="PS1 Feature 1: Get reconciled participation status from multiple sources"
)
async def get_participation_status(
    event_id: int,
    student_prn: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get canonical participation status for a student in an event.
    Resolves conflicts between registration, attendance, and certificate data.
    """
    service = ReconciliationService(db)
    status_data = service.get_canonical_status(event_id, student_prn)
    return status_data


@router.get(
    "/participation/conflicts/{event_id}",
    response_model=List[ConflictResponse],
    summary="Detect Event Conflicts",
    description="PS1 Feature 1: Detect all participation conflicts in an event"
)
async def get_event_conflicts(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all participation conflicts for an event.
    Returns students with conflicting data.
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.ORGANIZER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    service = ReconciliationService(db)
    conflicts = service.get_event_conflicts(event_id)
    return conflicts


# ============================================================================
# FEATURE 3: CERTIFICATE VERIFICATION
# ============================================================================

@router.get(
    "/verify/certificate/{certificate_id}",
    response_model=CertificateVerificationResponse,
    summary="Verify Certificate",
    description="PS1 Feature 3: Public certificate verification endpoint"
)
async def verify_certificate(
    certificate_id: str,
    verification_hash: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Public endpoint to verify certificate authenticity.
    Does not require authentication.
    """
    certificate = db.query(Certificate).filter_by(certificate_id=certificate_id).first()
    
    if not certificate:
        return CertificateVerificationResponse(
            authentic=False,
            certificate_id=certificate_id,
            revoked=False,
            verification_hash_valid=False,
            message="Certificate not found in system"
        )
    
    # Check if revoked
    if certificate.revoked:
        return CertificateVerificationResponse(
            authentic=False,
            certificate_id=certificate_id,
            student_prn=certificate.student_prn,
            event_title=certificate.event.title if certificate.event else None,
            issued_at=certificate.issued_at,
            revoked=True,
            revocation_reason=certificate.revocation_reason,
            verification_hash_valid=False,
            message="Certificate has been revoked"
        )
    
    # Verify hash if provided
    hash_valid = True
    if verification_hash and certificate.verification_hash:
        hash_valid = certificate.verification_hash == verification_hash
    
    # Get student name
    from app.models.student import Student
    student = db.query(Student).filter_by(prn=certificate.student_prn).first()
    
    return CertificateVerificationResponse(
        authentic=hash_valid,
        certificate_id=certificate.certificate_id,
        student_prn=certificate.student_prn,
        student_name=student.name if student else None,
        event_title=certificate.event.title if certificate.event else None,
        event_date=certificate.event.start_time if certificate.event else None,
        issued_at=certificate.issued_at,
        revoked=False,
        revocation_reason=None,
        verification_hash_valid=hash_valid,
        message="Certificate is authentic and valid" if hash_valid else "Certificate ID valid but hash mismatch"
    )


# ============================================================================
# FEATURE 4: REVOCATION & RETROACTIVE CHANGES
# ============================================================================

@router.post(
    "/certificate/{certificate_id}/revoke",
    summary="Revoke Certificate",
    description="PS1 Feature 4: Revoke a certificate with reason"
)
async def revoke_certificate(
    certificate_id: str,
    request: RevokeCertificateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Revoke a certificate with reason.
    Preserves history and prevents future use.
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.ORGANIZER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to revoke certificates"
        )
    
    certificate = db.query(Certificate).filter_by(certificate_id=certificate_id).first()
    
    if not certificate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Certificate not found"
        )
    
    if certificate.revoked:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Certificate is already revoked"
        )
    
    # Revoke certificate
    certificate.revoked = True
    certificate.revoked_at = datetime.utcnow()
    certificate.revoked_by = current_user.id
    certificate.revocation_reason = request.reason
    
    # Log audit trail
    from app.models.audit_log import AuditLog
    audit_log = AuditLog(
        event_id=certificate.event_id,
        user_id=current_user.id,
        action_type="certificate_revoked",
        details={
            "certificate_id": certificate.certificate_id,
            "student_prn": certificate.student_prn,
            "reason": request.reason,
            "revoked_at": certificate.revoked_at.isoformat()
        }
    )
    db.add(audit_log)
    
    db.commit()
    
    return {
        "status": "success",
        "message": "Certificate revoked successfully",
        "certificate_id": certificate_id,
        "revoked_at": certificate.revoked_at,
        "reason": request.reason
    }


# ============================================================================
# FEATURE 5: MULTI-ROLE PARTICIPATION
# ============================================================================

@router.post(
    "/roles/{event_id}/assign",
    response_model=RoleResponse,
    summary="Assign Event Role",
    description="PS1 Feature 5: Assign event-specific role to student"
)
async def assign_role(
    event_id: int,
    request: RoleAssignmentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Assign event-specific role to a student.
    A student can have multiple roles per event.
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.ORGANIZER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to assign roles"
        )
    
    # Validate role
    try:
        role_type = RoleType[request.role.upper()]
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Must be one of: {', '.join([r.value for r in RoleType])}"
        )
    
    # Create role assignment
    role_assignment = ParticipationRole(
        event_id=event_id,
        student_prn=request.student_prn,
        role=role_type,
        assigned_by=current_user.id,
        time_segment=request.time_segment
    )
    
    db.add(role_assignment)
    db.commit()
    db.refresh(role_assignment)
    
    # Log audit trail
    from app.models.audit_log import AuditLog
    audit_log = AuditLog(
        event_id=event_id,
        user_id=current_user.id,
        action_type="role_assigned",
        details={
            "student_prn": request.student_prn,
            "role": role_type.value,
            "time_segment": request.time_segment
        }
    )
    db.add(audit_log)
    db.commit()
    
    return RoleResponse(
        id=role_assignment.id,
        event_id=role_assignment.event_id,
        student_prn=role_assignment.student_prn,
        role=role_assignment.role.value,
        assigned_at=role_assignment.assigned_at,
        time_segment=role_assignment.time_segment
    )


@router.get(
    "/roles/{event_id}",
    response_model=List[RoleResponse],
    summary="Get Event Roles",
    description="PS1 Feature 5: Get all role assignments for an event"
)
async def get_event_roles(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all role assignments for an event.
    """
    roles = db.query(ParticipationRole).filter_by(event_id=event_id).all()
    
    return [
        RoleResponse(
            id=role.id,
            event_id=role.event_id,
            student_prn=role.student_prn,
            role=role.role.value,
            assigned_at=role.assigned_at,
            time_segment=role.time_segment
        )
        for role in roles
    ]


@router.get(
    "/roles/student/{student_prn}",
    response_model=List[RoleResponse],
    summary="Get Student Roles",
    description="PS1 Feature 5: Get all roles assigned to a student across events"
)
async def get_student_roles(
    student_prn: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all roles assigned to a student across all events.
    """
    roles = db.query(ParticipationRole).filter_by(student_prn=student_prn).all()
    
    return [
        RoleResponse(
            id=role.id,
            event_id=role.event_id,
            student_prn=role.student_prn,
            role=role.role.value,
            assigned_at=role.assigned_at,
            time_segment=role.time_segment
        )
        for role in roles
    ]


@router.delete(
    "/roles/{role_id}",
    summary="Remove Role Assignment",
    description="PS1 Feature 5: Remove a role assignment"
)
async def remove_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Remove a role assignment.
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.ORGANIZER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to remove roles"
        )
    
    role = db.query(ParticipationRole).filter_by(id=role_id).first()
    
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role assignment not found"
        )
    
    # Log before deletion
    from app.models.audit_log import AuditLog
    audit_log = AuditLog(
        event_id=role.event_id,
        user_id=current_user.id,
        action_type="role_removed",
        details={
            "role_id": role.id,
            "student_prn": role.student_prn,
            "role": role.role.value
        }
    )
    db.add(audit_log)
    
    db.delete(role)
    db.commit()
    
    return {
        "status": "success",
        "message": "Role assignment removed successfully"
    }


# ============================================================================
# PHASE 2: TRANSCRIPT GENERATOR
# ============================================================================

@router.get(
    "/transcript/{prn}",
    summary="Get participation transcript (JSON)",
    description="PS1 Phase 2: Get structured participation transcript data for a student"
)
async def get_transcript_data(
    prn: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get comprehensive participation transcript for a student.
    Returns JSON data including all participations, statistics, and roles.
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.ORGANIZER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to view transcripts"
        )
    
    service = TranscriptService(db)
    transcript_data = service.get_student_participations(prn)
    
    return transcript_data


@router.get(
    "/transcript/{prn}/pdf",
    summary="Download participation transcript as PDF",
    description="PS1 Phase 2: Generate and download PDF transcript"
)
async def download_transcript_pdf(
    prn: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate and download PDF transcript for a student.
    Returns PDF file as downloadable response.
    """
    from fastapi.responses import StreamingResponse
    
    if current_user.role not in [UserRole.ADMIN, UserRole.ORGANIZER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to generate transcripts"
        )
    
    service = TranscriptService(db)
    
    try:
        pdf_buffer = service.generate_transcript_pdf(prn)
        
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=transcript_{prn}.pdf"
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate PDF: {str(e)}"
        )


# ============================================================================
# PHASE 2: STUDENT SNAPSHOTS
# ============================================================================

@router.post(
    "/snapshots/{event_id}/capture",
    summary="Capture student snapshot",
    description="PS1 Phase 2: Capture current state of student profile"
)
async def capture_student_snapshot(
    event_id: int,
    student_prn: str,
    trigger: str = "manual",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Capture a snapshot of student's current profile and participation status.
    Usually triggered automatically on registration, but can be manual.
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.ORGANIZER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to capture snapshots"
        )
    
    service = SnapshotService(db)
    snapshot = service.capture_snapshot(student_prn, event_id, trigger)
    
    return {
        "id": snapshot.id,
        "student_prn": snapshot.student_prn,
        "event_id": snapshot.event_id,
        "captured_at": snapshot.captured_at,
        "trigger": snapshot.snapshot_trigger,
        "profile_data": snapshot.profile_data,
        "participation_status": snapshot.participation_status
    }


@router.get(
    "/snapshots/student/{prn}",
    summary="Get student snapshot history",
    description="PS1 Phase 2: Get all historical snapshots for a student"
)
async def get_student_snapshots(
    prn: str,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all historical snapshots for a student.
    Shows profile evolution over time.
    """
    service = SnapshotService(db)
    snapshots = service.get_student_history(prn, limit)
    
    return [
        {
            "id": s.id,
            "event_id": s.event_id,
            "captured_at": s.captured_at,
            "trigger": s.snapshot_trigger,
            "profile_data": s.profile_data,
            "participation_status": s.participation_status
        }
        for s in snapshots
    ]


@router.get(
    "/snapshots/student/{prn}/event/{event_id}",
    summary="Get snapshot at specific event",
    description="PS1 Phase 2: Get student profile as it was at event registration"
)
async def get_snapshot_at_event(
    prn: str,
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get student snapshot at the time of a specific event.
    Useful for retroactive analysis.
    """
    service = SnapshotService(db)
    snapshot = service.get_snapshot_at_event(prn, event_id)
    
    if not snapshot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No snapshot found for this student at this event"
        )
    
    return {
        "id": snapshot.id,
        "student_prn": snapshot.student_prn,
        "event_id": snapshot.event_id,
        "captured_at": snapshot.captured_at,
        "trigger": snapshot.snapshot_trigger,
        "profile_data": snapshot.profile_data,
        "participation_status": snapshot.participation_status
    }


@router.get(
    "/snapshots/compare/{snapshot1_id}/{snapshot2_id}",
    summary="Compare two snapshots",
    description="PS1 Phase 2: Compare student profile evolution between two snapshots"
)
async def compare_snapshots(
    snapshot1_id: int,
    snapshot2_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Compare two snapshots to see profile changes.
    Shows what changed between two points in time.
    """
    service = SnapshotService(db)
    comparison = service.compare_snapshots(snapshot1_id, snapshot2_id)
    
    if "error" in comparison:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=comparison["error"]
        )
    
    return comparison


# ============================================================================
# FEATURE 4: ATTENDANCE INVALIDATION (PS1 Phase 3)
# ============================================================================

@router.post(
    "/attendance/{attendance_id}/invalidate",
    summary="Invalidate Attendance Record",
    description="PS1 Feature 4: Mark an attendance record as invalid with reason"
)
async def invalidate_attendance(
    attendance_id: int,
    request: InvalidateAttendanceRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Invalidate an attendance record (e.g., mistaken scan, fraudulent attendance).
    Preserves the original record but marks it as invalid.
    Updates canonical status accordingly.
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.ORGANIZER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to invalidate attendance"
        )
    
    attendance = db.query(Attendance).filter_by(id=attendance_id).first()
    
    if not attendance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attendance record not found"
        )
    
    if attendance.invalidated:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Attendance record is already invalidated"
        )
    
    # Mark as invalidated
    attendance.invalidated = True
    attendance.invalidated_at = datetime.now(timezone.utc)
    attendance.invalidated_by = current_user.id
    attendance.invalidation_reason = request.reason
    
    # Log in audit trail
    from app.models.audit_log import AuditLog
    audit_log = AuditLog(
        event_id=attendance.event_id,
        user_id=current_user.id,
        action_type="attendance_invalidated",
        details={
            "attendance_id": attendance.id,
            "student_prn": attendance.student_prn,
            "scan_date": attendance.scanned_at.isoformat() if attendance.scanned_at else None,
            "day_number": attendance.day_number,
            "reason": request.reason,
            "invalidated_at": attendance.invalidated_at.isoformat()
        }
    )
    db.add(audit_log)
    
    db.commit()
    
    return {
        "status": "success",
        "message": "Attendance record invalidated successfully",
        "attendance_id": attendance_id,
        "student_prn": attendance.student_prn,
        "invalidated_at": attendance.invalidated_at,
        "reason": request.reason
    }


# ============================================================================
# FEATURE 4: CHANGE HISTORY & AUDIT TRAIL (PS1 Phase 3)
# ============================================================================

@router.get(
    "/audit/{event_id}/{student_prn}",
    summary="Get Change History",
    description="PS1 Feature 4: Get comprehensive change history for a student in an event"
)
async def get_change_history(
    event_id: int,
    student_prn: str,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get complete change history for a student in an event.
    Shows: certificate revocations, attendance invalidations, corrections, and all audit entries.
    Displays old vs new state for each change.
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.ORGANIZER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to view audit history"
        )
    
    service = AuditService(db)
    history = service.get_change_history(event_id, student_prn, limit)
    
    if "error" in history:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=history["error"]
        )
    
    return history


@router.get(
    "/audit/summary/{event_id}",
    summary="Get Event Audit Summary",
    description="PS1 Feature 4: Get audit summary for entire event"
)
async def get_event_audit_summary(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get audit summary for an entire event.
    Shows total revocations, invalidations, corrections across all students.
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.ORGANIZER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to view audit summary"
        )
    
    service = AuditService(db)
    summary = service.get_event_audit_summary(event_id)
    
    if "error" in summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=summary["error"]
        )
    
    return summary


# ============================================================================
# FEATURE 4: ORGANIZER CORRECTION WORKFLOW (PS1 Phase 3)
# ============================================================================

@router.post(
    "/participation/{event_id}/{student_prn}/correct",
    summary="Correct Participation Data",
    description="PS1 Feature 4: Apply manual correction to participation records"
)
async def correct_participation(
    event_id: int,
    student_prn: str,
    request: CorrectionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Apply manual correction to participation data.
    Logs the change with reason for audit trail.
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.ORGANIZER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to correct participation data"
        )
    
    service = AuditService(db)
    
    # Log the correction
    audit_log = service.log_correction(
        event_id=event_id,
        student_prn=student_prn,
        user_id=current_user.id,
        correction_type=request.correction_type,
        old_value=request.old_value,
        new_value=request.new_value,
        reason=request.reason
    )
    
    return {
        "status": "success",
        "message": "Correction applied and logged successfully",
        "audit_log_id": audit_log.id,
        "correction_type": request.correction_type,
        "old_value": request.old_value,
        "new_value": request.new_value,
        "corrected_by": current_user.email,
        "timestamp": audit_log.timestamp.isoformat()
    }


# ============================================================================
# FEATURE 3: FRAUD DETECTION (PS1 Phase 3)
# ============================================================================

@router.get(
    "/fraud/detect/{event_id}",
    summary="Detect Fraud Patterns",
    description="PS1 Feature 3: Run fraud detection algorithms on event data"
)
async def detect_fraud(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Run comprehensive fraud detection on event participation data.
    Detects:
    - Duplicate certificates
    - Certificates without participation
    - Suspicious timing patterns
    - Multiple scans in short time
    - Premature certificate issuance
    - Revoked certificate usage
    - Manual override abuse
    - Bulk upload anomalies
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.ORGANIZER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to run fraud detection"
        )
    
    service = FraudDetectionService(db)
    fraud_report = service.detect_fraud(event_id)
    
    return fraud_report


# ============================================================================
# FEATURE 3: QR CODE GENERATION FOR CERTIFICATES (PS1 Phase 3)
# ============================================================================

from fastapi.responses import StreamingResponse

@router.get(
    "/certificate/{certificate_id}/qr",
    summary="Generate Certificate QR Code",
    description="PS1 Feature 3: Generate QR code with verification link for a certificate"
)
async def get_certificate_qr_code(
    certificate_id: str,
    size: int = 300,
    format: str = "png"
):
    """
    Generate QR code for certificate verification.
    QR code contains verification URL that can be scanned.
    
    Public endpoint - no authentication required for verification QR codes.
    """
    try:
        if format == "base64":
            qr_data = generate_certificate_qr_code(
                certificate_id,
                size=size,
                return_base64=True
            )
            return {"qr_code": qr_data, "format": "base64"}
        else:
            qr_buffer = generate_certificate_qr_code(certificate_id, size=size)
            return StreamingResponse(
                qr_buffer,
                media_type="image/png",
                headers={
                    "Content-Disposition": f"inline; filename=cert_{certificate_id}_qr.png"
                }
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate QR code: {str(e)}"
        )


@router.get(
    "/transcript/{prn}/qr",
    summary="Generate Transcript QR Code",
    description="PS1 Feature 3: Generate QR code with transcript link for a student"
)
async def get_transcript_qr_code(
    prn: str,
    size: int = 200,
    format: str = "png"
):
    """
    Generate QR code for student transcript.
    QR code contains transcript URL that can be scanned.
    
    Public endpoint - transcripts are publicly verifiable.
    """
    try:
        if format == "base64":
            qr_data = generate_transcript_qr_code(
                prn,
                size=size,
                return_base64=True
            )
            return {"qr_code": qr_data, "format": "base64"}
        else:
            qr_buffer = generate_transcript_qr_code(prn, size=size)
            return StreamingResponse(
                qr_buffer,
                media_type="image/png",
                headers={
                    "Content-Disposition": f"inline; filename=transcript_{prn}_qr.png"
                }
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate QR code: {str(e)}"
        )


# ============================================================================
# FEATURE 1: BULK CONFLICT RESOLUTION (PS1 Phase 3)
# ============================================================================

@router.post(
    "/conflicts/{event_id}/bulk-resolve",
    response_model=BulkResolutionResponse,
    summary="Bulk Resolve Conflicts",
    description="PS1 Feature 1: Resolve multiple conflicts at once with specified actions"
)
async def bulk_resolve_conflicts(
    event_id: int,
    request: BulkResolutionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Bulk resolve conflicts for an event.
    
    Supported actions:
    - add_attendance: Add manual attendance record
    - revoke_certificate: Revoke the certificate
    - ignore: Mark as reviewed but no action taken
    - manual_review: Flag for manual review later
    
    Returns summary of actions taken and any failures.
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.ORGANIZER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to bulk resolve conflicts"
        )
    
    results = {
        "total_actions": len(request.actions),
        "successful": 0,
        "failed": 0,
        "details": []
    }
    
    from app.models.event import Event
    from app.models.ticket import Ticket
    from app.models.audit_log import AuditLog
    
    event = db.query(Event).filter_by(id=event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    for action_item in request.actions:
        try:
            student_prn = action_item.student_prn
            action = action_item.action
            reason = action_item.reason or "Bulk conflict resolution"
            
            if action == "add_attendance":
                ticket = db.query(Ticket).filter_by(
                    event_id=event_id,
                    student_prn=student_prn
                ).first()
                
                if not ticket:
                    results["details"].append({
                        "student_prn": student_prn,
                        "action": action,
                        "status": "failed",
                        "reason": "No registration found"
                    })
                    results["failed"] += 1
                    continue
                
                existing = db.query(Attendance).filter_by(
                    event_id=event_id,
                    student_prn=student_prn,
                    invalidated=False
                ).first()
                
                if existing:
                    results["successful"] += 1
                    continue
                
                attendance = Attendance(
                    ticket_id=ticket.id,
                    event_id=event_id,
                    student_prn=student_prn,
                    scanned_at=datetime.now(timezone.utc),
                    scan_source="admin_override",
                    scanner_id=current_user.id,
                    day_number=1
                )
                db.add(attendance)
                
                audit_log = AuditLog(
                    event_id=event_id,
                    user_id=current_user.id,
                    action_type="bulk_attendance_added",
                    details={"student_prn": student_prn, "reason": reason, "bulk_resolution": True}
                )
                db.add(audit_log)
                
                results["details"].append({"student_prn": student_prn, "action": action, "status": "success"})
                results["successful"] += 1
                
            elif action == "revoke_certificate":
                certificate = db.query(Certificate).filter_by(
                    event_id=event_id,
                    student_prn=student_prn,
                    revoked=False
                ).first()
                
                if not certificate:
                    results["failed"] += 1
                    continue
                
                certificate.revoked = True
                certificate.revoked_at = datetime.now(timezone.utc)
                certificate.revoked_by = current_user.id
                certificate.revocation_reason = reason
                
                audit_log = AuditLog(
                    event_id=event_id,
                    user_id=current_user.id,
                    action_type="bulk_certificate_revoked",
                    details={"student_prn": student_prn, "reason": reason, "bulk_resolution": True}
                )
                db.add(audit_log)
                
                results["details"].append({"student_prn": student_prn, "action": action, "status": "success"})
                results["successful"] += 1
                
            elif action in ["ignore", "manual_review"]:
                audit_log = AuditLog(
                    event_id=event_id,
                    user_id=current_user.id,
                    action_type=f"bulk_{action}",
                    details={"student_prn": student_prn, "reason": reason}
                )
                db.add(audit_log)
                results["successful"] += 1
                
            else:
                results["failed"] += 1
                
        except Exception as e:
            results["details"].append({"student_prn": action_item.student_prn, "status": "failed", "reason": str(e)})
            results["failed"] += 1
    
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to commit: {str(e)}"
        )
    
    return BulkResolutionResponse(**results)
