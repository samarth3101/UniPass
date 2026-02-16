"""
Role-Based Certificate Service Functions
Handles certificate issuance for different roles: Attendee, Organizer, Scanner, Volunteer
"""

from typing import Dict, List
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.models.certificate import Certificate
from app.models.attendance import Attendance
from app.models.volunteer import Volunteer
from app.models.student import Student
from app.models.event import Event
from app.models.user import User
from app.services.certificate_service import generate_certificate_id
from app.services.email_service import send_certificate_email


def issue_attendee_certificates(db: Session, event_id: int) -> Dict:
    """
    Issue certificates to students who attended the event
    Only students without existing attendee certificates
    """
    from app.services.certificate_service import get_students_without_certificates
    
    # Get event
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        return {"success": False, "error": "Event not found"}
    
    # Get students without certificates
    eligible = get_students_without_certificates(db, event_id)
    
    if not eligible:
        return {
            "success": True,
            "issued": 0,
            "emailed": 0,
            "failed": 0,
            "message": "No eligible attendees"
        }
    
    issued = 0
    emailed = 0
    failed = 0
    
    for student in eligible:
        try:
            cert_id = generate_certificate_id()
            
            # Create attendee certificate
            cert = Certificate(
                event_id=event_id,
                student_prn=student['prn'],
                certificate_id=cert_id,
                role_type='attendee',
                recipient_name=student['name'],
                recipient_email=student['email'],
                issued_at=datetime.now(timezone.utc)
            )
            
            # Generate verification hash
            cert.verification_hash = cert.generate_verification_hash()
            
            db.add(cert)
            db.flush()
            issued += 1
            
            # Send email
            if student['email']:
                event_date = event.start_time.strftime('%B %d, %Y') if event.start_time else 'TBD'
                success = send_certificate_email(
                    to_email=student['email'],
                    student_name=student['name'],
                    event_title=event.title,
                    event_location=event.location or 'TBD',
                    event_date=event_date,
                    certificate_id=cert_id,
                    role_type='attendee'
                )
                
                if success:
                    cert.email_sent = True
                    cert.email_sent_at = datetime.now(timezone.utc)
                    emailed += 1
                else:
                    failed += 1
        
        except Exception as e:
            print(f"Error issuing attendee certificate: {e}")
            failed += 1
    
    db.commit()
    
    return {
        "success": True,
        "issued": issued,
        "emailed": emailed,
        "failed": failed
    }


def issue_organizer_certificates(db: Session, event_id: int) -> Dict:
    """
    Issue certificates to event organizers
    Includes event creator and any assigned organizers
    """
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        return {"success": False, "error": "Event not found"}
    
    # Get event creator
    creator = db.query(User).filter(User.id == event.created_by).first()
    if not creator:
        return {
            "success": True,
            "issued": 0,
            "emailed": 0,
            "failed": 0,
            "message": "No organizer found"
        }
    
    # Check if organizer certificate already exists
    existing = db.query(Certificate).filter(
        Certificate.event_id == event_id,
        Certificate.role_type == 'organizer',
        Certificate.recipient_email == creator.email
    ).first()
    
    if existing:
        return {
            "success": True,
            "issued": 0,
            "emailed": 0,
            "failed": 0,
            "message": "Organizer certificate already issued"
        }
    
    issued = 0
    emailed = 0
    failed = 0
    
    try:
        cert_id = generate_certificate_id()
        
        # Create organizer certificate
        cert = Certificate(
            event_id=event_id,
            student_prn=None,  # Organizers may not be students
            certificate_id=cert_id,
            role_type='organizer',
            recipient_name=creator.full_name or creator.email,
            recipient_email=creator.email,
            issued_at=datetime.now(timezone.utc)
        )
        
        cert.verification_hash = cert.generate_verification_hash()
        
        db.add(cert)
        db.flush()
        issued += 1
        
        # Send email
        event_date = event.start_time.strftime('%B %d, %Y') if event.start_time else 'TBD'
        success = send_certificate_email(
            to_email=creator.email,
            student_name=creator.full_name or creator.email,
            event_title=event.title,
            event_location=event.location or 'TBD',
            event_date=event_date,
            certificate_id=cert_id,
            role_type='organizer'
        )
        
        if success:
            cert.email_sent = True
            cert.email_sent_at = datetime.now(timezone.utc)
            emailed += 1
        else:
            failed += 1
    
    except Exception as e:
        print(f"Error issuing organizer certificate: {e}")
        failed += 1
    
    db.commit()
    
    return {
        "success": True,
        "issued": issued,
        "emailed": emailed,
        "failed": failed
    }


def issue_scanner_certificates(db: Session, event_id: int) -> Dict:
    """
    Issue certificates to users who scanned attendees for this event
    """
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        return {"success": False, "error": "Event not found"}
    
    # Get unique scanner IDs from attendance records
    scanner_ids = db.query(Attendance.scanner_id).filter(
        Attendance.event_id == event_id,
        Attendance.scanner_id.isnot(None)
    ).distinct().all()
    
    if not scanner_ids:
        return {
            "success": True,
            "issued": 0,
            "emailed": 0,
            "failed": 0,
            "message": "No scanners found"
        }
    
    scanner_ids = [sid[0] for sid in scanner_ids]
    
    issued = 0
    emailed = 0
    failed = 0
    
    for scanner_id in scanner_ids:
        # Get scanner user
        scanner = db.query(User).filter(User.id == scanner_id).first()
        if not scanner:
            continue
        
        # Check if certificate already exists
        existing = db.query(Certificate).filter(
            Certificate.event_id == event_id,
            Certificate.role_type == 'scanner',
            Certificate.recipient_email == scanner.email
        ).first()
        
        if existing:
            continue
        
        try:
            cert_id = generate_certificate_id()
            
            # Create scanner certificate
            cert = Certificate(
                event_id=event_id,
                student_prn=None,  # Scanners may not be students
                certificate_id=cert_id,
                role_type='scanner',
                recipient_name=scanner.full_name or scanner.email,
                recipient_email=scanner.email,
                issued_at=datetime.now(timezone.utc)
            )
            
            cert.verification_hash = cert.generate_verification_hash()
            
            db.add(cert)
            db.flush()
            issued += 1
            
            # Send email
            event_date = event.start_time.strftime('%B %d, %Y') if event.start_time else 'TBD'
            success = send_certificate_email(
                to_email=scanner.email,
                student_name=scanner.full_name or scanner.email,
                event_title=event.title,
                event_location=event.location or 'TBD',
                event_date=event_date,
                certificate_id=cert_id,
                role_type='scanner'
            )
            
            if success:
                cert.email_sent = True
                cert.email_sent_at = datetime.now(timezone.utc)
                emailed += 1
            else:
                failed += 1
        
        except Exception as e:
            print(f"Error issuing scanner certificate: {e}")
            failed += 1
    
    db.commit()
    
    return {
        "success": True,
        "issued": issued,
        "emailed": emailed,
        "failed": failed
    }


def issue_volunteer_certificates(db: Session, event_id: int) -> Dict:
    """
    Issue certificates to volunteers who haven't received one yet
    """
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        return {"success": False, "error": "Event not found"}
    
    # Get volunteers without certificates
    volunteers = db.query(Volunteer).filter(
        Volunteer.event_id == event_id,
        Volunteer.certificate_sent == False
    ).all()
    
    if not volunteers:
        return {
            "success": True,
            "issued": 0,
            "emailed": 0,
            "failed": 0,
            "message": "No volunteers pending certificates"
        }
    
    issued = 0
    emailed = 0
    failed = 0
    
    for volunteer in volunteers:
        try:
            cert_id = generate_certificate_id()
            
            # Create volunteer certificate
            cert = Certificate(
                event_id=event_id,
                student_prn=None,  # Volunteers don't have PRNs
                certificate_id=cert_id,
                role_type='volunteer',
                recipient_name=volunteer.name,
                recipient_email=volunteer.email,
                issued_at=datetime.now(timezone.utc)
            )
            
            cert.verification_hash = cert.generate_verification_hash()
            
            db.add(cert)
            db.flush()
            issued += 1
            
            # Send email
            event_date = event.start_time.strftime('%B %d, %Y') if event.start_time else 'TBD'
            success = send_certificate_email(
                to_email=volunteer.email,
                student_name=volunteer.name,
                event_title=event.title,
                event_location=event.location or 'TBD',
                event_date=event_date,
                certificate_id=cert_id,
                role_type='volunteer'
            )
            
            if success:
                cert.email_sent = True
                cert.email_sent_at = datetime.now(timezone.utc)
                volunteer.certificate_sent = True
                volunteer.certificate_sent_at = datetime.now(timezone.utc)
                emailed += 1
            else:
                failed += 1
        
        except Exception as e:
            print(f"Error issuing volunteer certificate: {e}")
            failed += 1
    
    db.commit()
    
    return {
        "success": True,
        "issued": issued,
        "emailed": emailed,
        "failed": failed
    }
