"""
Student Snapshot Service
Manages creation and retrieval of historical student snapshots
"""

from sqlalchemy.orm import Session
from typing import Dict, Any, Optional, List
from datetime import datetime

from app.models.student_snapshot import StudentSnapshot
from app.models.ticket import Ticket
from app.models.student import Student
from app.models.attendance import Attendance
from app.models.certificate import Certificate
from app.models.participation_role import ParticipationRole


class SnapshotService:
    """Service for managing student snapshots"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def capture_snapshot(
        self, 
        student_prn: str, 
        event_id: int,
        trigger: str = "registration"
    ) -> StudentSnapshot:
        """
        Capture current state of student profile
        Called automatically on registration or manually
        """
        # Get student profile from database
        student = self.db.query(Student).filter(
            Student.prn == student_prn
        ).first()
        
        if not student:
            # Create minimal profile if student doesn't exist
            profile_data = {
                "prn": student_prn,
                "captured_from": "minimal",
                "note": "Student not found in database"
            }
        else:
            # Build profile from student data
            profile_data = {
                "prn": student.prn,
                "name": student.name,
                "email": student.email,
                "branch": student.branch,
                "year": student.year,
                "division": student.division,
                "captured_from": "student_table"
            }
        
        # Calculate participation status
        participation_status = self._calculate_participation_status(student_prn)
        
        # Create snapshot
        snapshot = StudentSnapshot(
            student_prn=student_prn,
            event_id=event_id,
            captured_at=datetime.now(),
            snapshot_trigger=trigger,
            profile_data=profile_data,
            participation_status=participation_status
        )
        
        self.db.add(snapshot)
        self.db.commit()
        self.db.refresh(snapshot)
        
        return snapshot
    
    def _calculate_participation_status(self, student_prn: str) -> Dict[str, Any]:
        """Calculate aggregated participation stats for student"""
        # Count registrations
        total_events = self.db.query(Ticket).filter(
            Ticket.student_prn == student_prn
        ).count()
        
        # Count attendances
        attended_events = self.db.query(Attendance).filter(
            Attendance.student_prn == student_prn
        ).count()
        
        # Count certificates
        certificates_earned = self.db.query(Certificate).filter(
            Certificate.student_prn == student_prn,
            Certificate.revoked == False
        ).count()
        
        # Get roles
        roles = self.db.query(ParticipationRole.role).filter(
            ParticipationRole.student_prn == student_prn
        ).distinct().all()
        roles_held = [r[0].value for r in roles]
        
        # Get last participation
        last_attendance = self.db.query(Attendance).filter(
            Attendance.student_prn == student_prn
        ).order_by(Attendance.scan_time.desc()).first()
        
        return {
            "total_events": total_events,
            "attended_events": attended_events,
            "certificates_earned": certificates_earned,
            "roles_held": roles_held,
            "last_participation": last_attendance.scan_time.isoformat() if last_attendance else None,
            "calculated_at": datetime.now().isoformat()
        }
    
    def get_snapshot_at_event(
        self, 
        student_prn: str, 
        event_id: int
    ) -> Optional[StudentSnapshot]:
        """Get snapshot for student at specific event"""
        return self.db.query(StudentSnapshot).filter(
            StudentSnapshot.student_prn == student_prn,
            StudentSnapshot.event_id == event_id
        ).order_by(StudentSnapshot.captured_at.desc()).first()
    
    def get_student_history(
        self, 
        student_prn: str,
        limit: int = 50
    ) -> List[StudentSnapshot]:
        """Get all snapshots for a student in chronological order"""
        return self.db.query(StudentSnapshot).filter(
            StudentSnapshot.student_prn == student_prn
        ).order_by(StudentSnapshot.captured_at.desc()).limit(limit).all()
    
    def get_snapshot_by_date(
        self,
        student_prn: str,
        as_of_date: datetime
    ) -> Optional[StudentSnapshot]:
        """
        Get student snapshot as of a specific date
        Returns the most recent snapshot before or on that date
        """
        return self.db.query(StudentSnapshot).filter(
            StudentSnapshot.student_prn == student_prn,
            StudentSnapshot.captured_at <= as_of_date
        ).order_by(StudentSnapshot.captured_at.desc()).first()
    
    def compare_snapshots(
        self,
        snapshot1_id: int,
        snapshot2_id: int
    ) -> Dict[str, Any]:
        """
        Compare two snapshots to show profile evolution
        Returns differences between snapshots
        """
        snap1 = self.db.query(StudentSnapshot).filter_by(id=snapshot1_id).first()
        snap2 = self.db.query(StudentSnapshot).filter_by(id=snapshot2_id).first()
        
        if not snap1 or not snap2:
            return {"error": "One or both snapshots not found"}
        
        if snap1.student_prn != snap2.student_prn:
            return {"error": "Snapshots belong to different students"}
        
        # Compare profile data
        profile_diff = self._deep_diff(snap1.profile_data, snap2.profile_data)
        
        # Compare participation status
        status_diff = self._deep_diff(
            snap1.participation_status or {}, 
            snap2.participation_status or {}
        )
        
        return {
            "student_prn": snap1.student_prn,
            "snapshot1": {
                "id": snap1.id,
                "captured_at": snap1.captured_at.isoformat(),
                "event_id": snap1.event_id
            },
            "snapshot2": {
                "id": snap2.id,
                "captured_at": snap2.captured_at.isoformat(),
                "event_id": snap2.event_id
            },
            "profile_changes": profile_diff,
            "participation_changes": status_diff,
            "time_elapsed_days": (snap2.captured_at - snap1.captured_at).days
        }
    
    def _deep_diff(self, dict1: Dict, dict2: Dict) -> Dict[str, Any]:
        """Calculate differences between two dictionaries"""
        changes = {}
        all_keys = set(dict1.keys()) | set(dict2.keys())
        
        for key in all_keys:
            val1 = dict1.get(key)
            val2 = dict2.get(key)
            
            if val1 != val2:
                changes[key] = {
                    "old": val1,
                    "new": val2
                }
        
        return changes
