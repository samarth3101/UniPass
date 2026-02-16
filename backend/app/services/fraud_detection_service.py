"""
Fraud Detection Service - PS1 Feature 3
Verifiable Certificate & Transcript System - Fraud Detection Component

Detects suspicious patterns and potential fraud in participation records.
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from typing import Dict, List
from datetime import datetime, timedelta, timezone
from collections import defaultdict

from app.models.certificate import Certificate
from app.models.attendance import Attendance
from app.models.ticket import Ticket
from app.models.audit_log import AuditLog
from app.models.event import Event


class FraudType:
    """Types of fraud that can be detected"""
    DUPLICATE_CERTIFICATE = "DUPLICATE_CERTIFICATE"
    CERTIFICATE_WITHOUT_PARTICIPATION = "CERTIFICATE_WITHOUT_PARTICIPATION"
    SUSPICIOUS_TIMING = "SUSPICIOUS_TIMING"
    MULTIPLE_SCANS_SAME_MINUTE = "MULTIPLE_SCANS_SAME_MINUTE"
    CERTIFICATE_BEFORE_EVENT = "CERTIFICATE_BEFORE_EVENT"
    REVOKED_STILL_IN_USE = "REVOKED_STILL_IN_USE"
    MANUAL_OVERRIDE_ABUSE = "MANUAL_OVERRIDE_ABUSE"
    BULK_UPLOAD_ANOMALY = "BULK_UPLOAD_ANOMALY"


class FraudDetectionService:
    """
    Detects fraudulent or suspicious patterns in participation data
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def detect_fraud(self, event_id: int) -> Dict:
        """
        Run all fraud detection rules for an event.
        
        Returns:
            {
                "event_id": 123,
                "fraud_alerts": [
                    {
                        "type": "DUPLICATE_CERTIFICATE",
                        "severity": "HIGH",
                        "student_prn": "PRN001",
                        "description": "...",
                        "evidence": {...}
                    }
                ],
                "summary": {
                    "total_alerts": 5,
                    "high_severity": 2,
                    "medium_severity": 2,
                    "low_severity": 1
                }
            }
        """
        
        alerts = []
        
        # Rule 1: Duplicate certificates for same student
        alerts.extend(self._detect_duplicate_certificates(event_id))
        
        # Rule 2: Certificates without any participation signal
        alerts.extend(self._detect_orphan_certificates(event_id))
        
        # Rule 3: Multiple scans in same minute (same device)
        alerts.extend(self._detect_rapid_scans(event_id))
        
        # Rule 4: Certificates issued before event date
        alerts.extend(self._detect_premature_certificates(event_id))
        
        # Rule 5: Revoked certificates still being verified
        alerts.extend(self._detect_revoked_usage(event_id))
        
        # Rule 6: Excessive manual overrides
        alerts.extend(self._detect_override_abuse(event_id))
        
        # Rule 7: Suspicious bulk upload patterns
        alerts.extend(self._detect_bulk_anomalies(event_id))
        
        # Calculate summary
        summary = {
            "total_alerts": len(alerts),
            "high_severity": sum(1 for a in alerts if a['severity'] == 'HIGH'),
            "medium_severity": sum(1 for a in alerts if a['severity'] == 'MEDIUM'),
            "low_severity": sum(1 for a in alerts if a['severity'] == 'LOW'),
            "critical_types": list(set(a['type'] for a in alerts if a['severity'] == 'HIGH'))
        }
        
        return {
            "event_id": event_id,
            "fraud_alerts": alerts,
            "summary": summary,
            "scanned_at": datetime.now(timezone.utc).isoformat()
        }
    
    def _detect_duplicate_certificates(self, event_id: int) -> List[Dict]:
        """Detect students with multiple certificates for same event"""
        alerts = []
        
        # Group by student_prn and count (exclude role-based certificates with NULL student_prn)
        duplicates = self.db.query(
            Certificate.student_prn,
            func.count(Certificate.id).label('cert_count')
        ).filter(
            Certificate.event_id == event_id,
            Certificate.student_prn.isnot(None)  # Exclude organizer/scanner/volunteer certificates
        ).group_by(
            Certificate.student_prn
        ).having(
            func.count(Certificate.id) > 1
        ).all()
        
        for dup in duplicates:
            certs = self.db.query(Certificate).filter_by(
                event_id=event_id,
                student_prn=dup.student_prn
            ).all()
            
            alerts.append({
                "type": FraudType.DUPLICATE_CERTIFICATE,
                "severity": "HIGH",
                "student_prn": dup.student_prn,
                "description": f"Student has {dup.cert_count} certificates for same event",
                "evidence": {
                    "certificate_ids": [c.certificate_id for c in certs],
                    "issued_dates": [c.issued_at.isoformat() if c.issued_at else None for c in certs]
                },
                "recommendation": "Revoke duplicate certificates and investigate"
            })
        
        return alerts
    
    def _detect_orphan_certificates(self, event_id: int) -> List[Dict]:
        """Detect certificates issued without registration or attendance"""
        alerts = []
        
        # Only check student certificates (exclude organizer/scanner/volunteer role-based certificates)
        certificates = self.db.query(Certificate).filter(
            Certificate.event_id == event_id,
            Certificate.revoked == False,
            Certificate.student_prn.isnot(None)  # Exclude role-based certificates
        ).all()
        
        for cert in certificates:
            # Check if student has ticket (registration)
            has_ticket = self.db.query(Ticket).filter_by(
                event_id=event_id,
                student_prn=cert.student_prn
            ).first() is not None
            
            # Check if student has attendance
            has_attendance = self.db.query(Attendance).filter_by(
                event_id=event_id,
                student_prn=cert.student_prn,
                invalidated=False
            ).first() is not None
            
            if not has_ticket and not has_attendance:
                alerts.append({
                    "type": FraudType.CERTIFICATE_WITHOUT_PARTICIPATION,
                    "severity": "HIGH",
                    "student_prn": cert.student_prn,
                    "description": "Certificate issued without registration or attendance",
                    "evidence": {
                        "certificate_id": cert.certificate_id,
                        "issued_at": cert.issued_at.isoformat() if cert.issued_at else None,
                        "has_registration": False,
                        "has_attendance": False
                    },
                    "recommendation": "Verify certificate authenticity and revoke if fraudulent"
                })
            elif not has_attendance:
                alerts.append({
                    "type": FraudType.CERTIFICATE_WITHOUT_PARTICIPATION,
                    "severity": "MEDIUM",
                    "student_prn": cert.student_prn,
                    "description": "Certificate issued without attendance record",
                    "evidence": {
                        "certificate_id": cert.certificate_id,
                        "has_registration": True,
                        "has_attendance": False
                    },
                    "recommendation": "Check if attendance was recorded manually"
                })
        
        return alerts
    
    def _detect_rapid_scans(self, event_id: int) -> List[Dict]:
        """Detect multiple scans in very short time (potential device cloning)"""
        alerts = []
        
        # Get all attendance records ordered by time
        attendance_records = self.db.query(Attendance).filter_by(
            event_id=event_id,
            invalidated=False
        ).order_by(Attendance.scanned_at).all()
        
        # Group by minute
        scans_by_minute = defaultdict(list)
        for att in attendance_records:
            if att.scanned_at:
                minute_key = att.scanned_at.replace(second=0, microsecond=0)
                scans_by_minute[minute_key].append(att)
        
        # Detect suspicious patterns
        for minute, scans in scans_by_minute.items():
            if len(scans) > 10:  # More than 10 scans in same minute
                unique_students = len(set(s.student_prn for s in scans))
                if unique_students < len(scans) * 0.8:  # Duplicate scans
                    alerts.append({
                        "type": FraudType.MULTIPLE_SCANS_SAME_MINUTE,
                        "severity": "MEDIUM",
                        "student_prn": "MULTIPLE",
                        "description": f"{len(scans)} scans in 1 minute with only {unique_students} unique students",
                        "evidence": {
                            "timestamp": minute.isoformat(),
                            "total_scans": len(scans),
                            "unique_students": unique_students,
                            "scan_sources": list(set(s.scan_source for s in scans))
                        },
                        "recommendation": "Review scanner behavior and device fingerprints"
                    })
        
        return alerts
    
    def _detect_premature_certificates(self, event_id: int) -> List[Dict]:
        """Detect certificates issued before event start date"""
        alerts = []
        
        event = self.db.query(Event).filter_by(id=event_id).first()
        if not event or not event.start_time:
            return alerts
        
        premature_certs = self.db.query(Certificate).filter(
            and_(
                Certificate.event_id == event_id,
                Certificate.issued_at < event.start_time,
                Certificate.revoked == False
            )
        ).all()
        
        for cert in premature_certs:
            alerts.append({
                "type": FraudType.CERTIFICATE_BEFORE_EVENT,
                "severity": "HIGH",
                "student_prn": cert.student_prn,
                "description": "Certificate issued before event started",
                "evidence": {
                    "certificate_id": cert.certificate_id,
                    "issued_at": cert.issued_at.isoformat() if cert.issued_at else None,
                    "event_start": event.start_time.isoformat() if event.start_time else None,
                    "days_before": (event.start_time - cert.issued_at).days if cert.issued_at else None
                },
                "recommendation": "Revoke certificate and investigate issuance process"
            })
        
        return alerts
    
    def _detect_revoked_usage(self, event_id: int) -> List[Dict]:
        """Detect attempts to verify revoked certificates"""
        alerts = []
        
        # Check audit logs for verification attempts on revoked certificates
        revoked_certs = self.db.query(Certificate).filter_by(
            event_id=event_id,
            revoked=True
        ).all()
        
        for cert in revoked_certs:
            # Check if there are verification attempts after revocation
            verification_logs = self.db.query(AuditLog).filter(
                and_(
                    AuditLog.event_id == event_id,
                    AuditLog.action_type == 'certificate_verified',
                    AuditLog.timestamp > cert.revoked_at
                )
            ).all()
            
            relevant_logs = [
                log for log in verification_logs 
                if log.details and log.details.get('certificate_id') == cert.certificate_id
            ]
            
            if relevant_logs:
                alerts.append({
                    "type": FraudType.REVOKED_STILL_IN_USE,
                    "severity": "HIGH",
                    "student_prn": cert.student_prn,
                    "description": f"Revoked certificate verified {len(relevant_logs)} times after revocation",
                    "evidence": {
                        "certificate_id": cert.certificate_id,
                        "revoked_at": cert.revoked_at.isoformat() if cert.revoked_at else None,
                        "verification_attempts": len(relevant_logs),
                        "last_attempt": relevant_logs[-1].timestamp.isoformat() if relevant_logs else None
                    },
                    "recommendation": "Alert relevant authorities about potential fraud"
                })
        
        return alerts
    
    def _detect_override_abuse(self, event_id: int) -> List[Dict]:
        """Detect excessive use of manual attendance overrides"""
        alerts = []
        
        # Count overrides by scanner
        overrides = self.db.query(
            Attendance.scanner_id,
            func.count(Attendance.id).label('override_count')
        ).filter(
            and_(
                Attendance.event_id == event_id,
                Attendance.scan_source == 'admin_override'
            )
        ).group_by(Attendance.scanner_id).all()
        
        for override in overrides:
            if override.override_count > 20:  # Threshold: 20+ overrides
                alerts.append({
                    "type": FraudType.MANUAL_OVERRIDE_ABUSE,
                    "severity": "MEDIUM",
                    "student_prn": "N/A",
                    "description": f"Scanner {override.scanner_id} used {override.override_count} manual overrides",
                    "evidence": {
                        "scanner_id": override.scanner_id,
                        "override_count": override.override_count
                    },
                    "recommendation": "Review scanner permissions and override justifications"
                })
        
        return alerts
    
    def _detect_bulk_anomalies(self, event_id: int) -> List[Dict]:
        """Detect suspicious bulk upload patterns"""
        alerts = []
        
        # Find bulk uploads with unusual timing
        bulk_uploads = self.db.query(Attendance).filter(
            and_(
                Attendance.event_id == event_id,
                Attendance.scan_source == 'bulk_upload'
            )
        ).all()
        
        # Group by minute
        uploads_by_minute = defaultdict(list)
        for att in bulk_uploads:
            if att.scanned_at:
                minute_key = att.scanned_at.replace(second=0, microsecond=0)
                uploads_by_minute[minute_key].append(att)
        
        for minute, uploads in uploads_by_minute.items():
            if len(uploads) > 100:  # More than 100 records in 1 minute
                alerts.append({
                    "type": FraudType.BULK_UPLOAD_ANOMALY,
                    "severity": "LOW",
                    "student_prn": "N/A",
                    "description": f"Bulk upload of {len(uploads)} records in 1 minute",
                    "evidence": {
                        "timestamp": minute.isoformat(),
                        "record_count": len(uploads),
                        "scanner_ids": list(set(u.scanner_id for u in uploads if u.scanner_id))
                    },
                    "recommendation": "Verify bulk upload source and data integrity"
                })
        
        return alerts
