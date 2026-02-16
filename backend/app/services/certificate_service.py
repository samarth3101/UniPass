"""
Certificate Service
Handles certificate generation and distribution for event attendees
"""

import uuid
from typing import List, Dict
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.certificate import Certificate
from app.models.attendance import Attendance
from app.models.ticket import Ticket
from app.models.student import Student
from app.models.event import Event
from app.services.email_service import send_certificate_email


def generate_certificate_id() -> str:
    """Generate a unique certificate ID"""
    return f"CERT-{uuid.uuid4().hex[:12].upper()}"


def get_eligible_students(db: Session, event_id: int) -> List[Dict]:
    """
    Get list of students eligible for certificates (attended ALL days of the event)
    For multi-day events: student must attend all days to be eligible
    Returns list of student details with attendance information
    """
    # Get event details to check total_days
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        return []
    
    total_days = event.total_days or 1
    
    # Get all attendance records for this event
    from sqlalchemy import func
    
    # Find students who attended all required days
    # Group by student_prn and count distinct days attended
    attendance_summary = db.query(
        Attendance.student_prn,
        func.count(func.distinct(Attendance.day_number)).label('days_attended'),
        func.min(Attendance.scanned_at).label('first_scan')
    ).filter(
        Attendance.event_id == event_id
    ).group_by(
        Attendance.student_prn
    ).all()
    
    eligible_students = []
    
    for record in attendance_summary:
        # Only include students who attended ALL days
        if record.days_attended >= total_days:
            # Get student details
            student = db.query(Student).filter(Student.prn == record.student_prn).first()
            
            if student:
                eligible_students.append({
                    "prn": student.prn,
                    "name": student.name,
                    "email": student.email,
                    "scanned_at": record.first_scan,
                    "days_attended": record.days_attended,
                    "total_days": total_days
                })
    
    return eligible_students


def get_students_without_certificates(db: Session, event_id: int) -> List[Dict]:
    """
    Get list of students who attended but haven't received certificates yet
    """
    # Get all eligible students
    eligible_students = get_eligible_students(db, event_id)
    
    # Get students who already have certificates
    existing_certificates = db.query(Certificate).filter(
        Certificate.event_id == event_id
    ).all()
    
    certified_prns = {cert.student_prn for cert in existing_certificates}
    
    # Filter out students who already have certificates
    students_without_certs = [
        student for student in eligible_students 
        if student["prn"] not in certified_prns
    ]
    
    return students_without_certs


def issue_certificates(
    db: Session, 
    event_id: int,
    dry_run: bool = False
) -> Dict:
    """
    Issue certificates to all eligible students who haven't received one yet
    
    Args:
        db: Database session
        event_id: Event ID
        dry_run: If True, only return who would get certificates without actually sending
    
    Returns:
        Dictionary with results including success count, failures, and skipped
    """
    # Get event details
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        return {
            "success": False,
            "error": "Event not found"
        }
    
    # Get students who need certificates
    students_to_certify = get_students_without_certificates(db, event_id)
    
    if not students_to_certify:
        return {
            "success": True,
            "message": "No new certificates to issue",
            "total_eligible": 0,
            "certificates_issued": 0,
            "emails_sent": 0,
            "emails_failed": 0
        }
    
    # If dry run, just return the list
    if dry_run:
        return {
            "success": True,
            "dry_run": True,
            "total_eligible": len(students_to_certify),
            "students": students_to_certify
        }
    
    # Issue certificates
    certificates_issued = 0
    emails_sent = 0
    emails_failed = 0
    failed_students = []
    
    for student in students_to_certify:
        try:
            # Generate certificate ID
            cert_id = generate_certificate_id()
            
            # Create certificate record
            certificate = Certificate(
                event_id=event_id,
                student_prn=student["prn"],
                certificate_id=cert_id,
                email_sent=False
            )
            
            db.add(certificate)
            db.flush()  # Assign ID without committing
            
            # Generate verification hash (PS1 Feature 3)
            certificate.verification_hash = certificate.generate_verification_hash()
            
            certificates_issued += 1
            
            # Send email if student has email
            if student["email"]:
                event_date = event.start_time.strftime('%B %d, %Y')
                
                email_sent = send_certificate_email(
                    to_email=student["email"],
                    student_name=student["name"],
                    event_title=event.title,
                    event_location=event.location,
                    event_date=event_date,
                    certificate_id=cert_id
                )
                
                if email_sent:
                    certificate.email_sent = True
                    certificate.email_sent_at = datetime.utcnow()
                    emails_sent += 1
                else:
                    emails_failed += 1
                    failed_students.append({
                        "prn": student["prn"],
                        "name": student["name"],
                        "email": student["email"],
                        "reason": "Email sending failed"
                    })
            else:
                # No email address
                failed_students.append({
                    "prn": student["prn"],
                    "name": student["name"],
                    "email": None,
                    "reason": "No email address"
                })
        
        except Exception as e:
            emails_failed += 1
            failed_students.append({
                "prn": student["prn"],
                "name": student["name"],
                "email": student.get("email"),
                "reason": str(e)
            })
    
    # Commit all changes
    db.commit()
    
    return {
        "success": True,
        "message": f"Issued {certificates_issued} certificates",
        "total_eligible": len(students_to_certify),
        "certificates_issued": certificates_issued,
        "emails_sent": emails_sent,
        "emails_failed": emails_failed,
        "failed_students": failed_students if failed_students else []
    }


def get_certificate_statistics(db: Session, event_id: int) -> Dict:
    """
    Get certificate statistics for an event
    """
    # Total registered
    total_registered = db.query(Ticket).filter(
        Ticket.event_id == event_id
    ).count()
    
    # Total attended (eligible for certificates)
    total_attended = db.query(Attendance).filter(
        Attendance.event_id == event_id
    ).distinct(Attendance.student_prn).count()
    
    # Total certificates issued
    total_certificates = db.query(Certificate).filter(
        Certificate.event_id == event_id
    ).count()
    
    # Certificates with emails sent
    certificates_emailed = db.query(Certificate).filter(
        Certificate.event_id == event_id,
        Certificate.email_sent == True
    ).count()
    
    # Students who attended but don't have certificates yet
    pending_certificates = len(get_students_without_certificates(db, event_id))
    
    return {
        "event_id": event_id,
        "total_registered": total_registered,
        "total_attended": total_attended,
        "total_certificates_issued": total_certificates,
        "certificates_emailed": certificates_emailed,
        "pending_certificates": pending_certificates,
        "can_push_certificates": pending_certificates > 0
    }


def is_student_eligible_for_certificate(db: Session, event_id: int, student_prn: str) -> bool:
    """
    Check if a specific student is eligible for a certificate
    For multi-day events: student must have attended ALL days
    
    Returns:
        True if student attended all required days, False otherwise
    """
    # Get event details
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        return False
    
    total_days = event.total_days or 1
    
    # Count distinct days attended by this student
    from sqlalchemy import func
    attended_days = db.query(
        func.count(func.distinct(Attendance.day_number))
    ).filter(
        Attendance.event_id == event_id,
        Attendance.student_prn == student_prn
    ).scalar()
    
    # Student must attend all days to be eligible
    return attended_days >= total_days
