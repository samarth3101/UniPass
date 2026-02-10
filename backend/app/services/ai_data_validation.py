"""
AI Data Validation Service
Phase 0 - AI Readiness

Ensures data quality before AI processing.
Detects duplicates, orphaned records, and generates data quality reports.
"""

from sqlalchemy import func
from sqlalchemy.orm import Session
from datetime import datetime

# Import models - use models module to avoid import issues
from app import models


class AIDataValidator:
    """Ensures data quality before AI processing"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def check_duplicate_scans(self) -> dict:
        """
        Detect duplicate attendance scans
        
        Returns:
            dict: Count and list of duplicate scans
        """
        duplicates = self.db.query(
            models.Attendance.event_id,
            models.Attendance.student_prn,
            func.count(models.Attendance.id).label('scan_count')
        ).group_by(
            models.Attendance.event_id,
            models.Attendance.student_prn
        ).having(
            func.count(models.Attendance.id) > 1
        ).all()
        
        return {
            'duplicate_count': len(duplicates),
            'duplicates': [
                {
                    'event_id': d.event_id,
                    'student_prn': d.student_prn,
                    'scan_count': d.scan_count
                }
                for d in duplicates
            ],
            'recommendation': 'Keep first scan, mark others as scan_source=ADMIN_OVERRIDE' if duplicates else 'No action needed'
        }
    
    def check_orphaned_attendance(self) -> dict:
        """
        Find attendance records without valid events/students
        
        Returns:
            dict: Count of orphaned records and cleanup status
        """
        # Check for attendance with invalid event_id
        orphaned_events = self.db.query(models.Attendance)\
            .outerjoin(models.Event, models.Attendance.event_id == models.Event.id)\
            .filter(models.Event.id == None)\
            .all()
        
        # Check for attendance with invalid student_prn
        orphaned_students = self.db.query(models.Attendance)\
            .outerjoin(models.Student, models.Attendance.student_prn == models.Student.prn)\
            .filter(models.Student.prn == None)\
            .all()
        
        total_orphaned = len(orphaned_events) + len(orphaned_students)
        
        return {
            'orphaned_count': total_orphaned,
            'orphaned_events': len(orphaned_events),
            'orphaned_students': len(orphaned_students),
            'needs_cleanup': total_orphaned > 0,
            'orphaned_event_ids': [a.id for a in orphaned_events[:10]],  # First 10
            'orphaned_student_ids': [a.id for a in orphaned_students[:10]],  # First 10
            'recommendation': 'Delete orphaned records or fix references' if total_orphaned > 0 else 'No action needed'
        }
    
    def get_data_statistics(self) -> dict:
        """
        Generate data quality report for AI readiness
        
        Returns:
            dict: Comprehensive data statistics
        """
        total_events = self.db.query(func.count(models.Event.id)).scalar() or 0
        total_students = self.db.query(func.count(models.Student.prn)).scalar() or 0
        total_attendance = self.db.query(func.count(models.Attendance.id)).scalar() or 0
        
        # Get date range
        earliest_event = self.db.query(func.min(models.Event.start_time)).scalar()
        latest_event = self.db.query(func.max(models.Event.start_time)).scalar()
        
        # Events with attendance
        events_with_attendance = self.db.query(
            func.count(func.distinct(models.Attendance.event_id))
        ).scalar() or 0
        
        # Average attendance per event
        avg_attendance = total_attendance / total_events if total_events > 0 else 0
        
        # Events with capacity data (for AI)
        events_with_capacity = self.db.query(func.count(models.Event.id))\
            .filter(models.Event.capacity != None)\
            .scalar() or 0
        
        # Events with type data (for AI)
        events_with_type = self.db.query(func.count(models.Event.id))\
            .filter(models.Event.event_type != None)\
            .scalar() or 0
        
        # Students with branch/year data (for AI)
        students_with_branch = self.db.query(func.count(models.Student.prn))\
            .filter(models.Student.branch != None)\
            .scalar() or 0
        
        students_with_year = self.db.query(func.count(models.Student.prn))\
            .filter(models.Student.year != None)\
            .scalar() or 0
        
        return {
            'total_events': total_events,
            'total_students': total_students,
            'total_attendance': total_attendance,
            'avg_attendance_per_event': round(avg_attendance, 2),
            'date_range': {
                'earliest': earliest_event.isoformat() if earliest_event else None,
                'latest': latest_event.isoformat() if latest_event else None,
                'span_days': (latest_event - earliest_event).days if earliest_event and latest_event else 0
            },
            'events_with_attendance': events_with_attendance,
            'events_without_attendance': total_events - events_with_attendance,
            'ai_readiness': {
                'events_with_capacity': events_with_capacity,
                'capacity_coverage': round((events_with_capacity / total_events * 100), 2) if total_events > 0 else 0,
                'events_with_type': events_with_type,
                'type_coverage': round((events_with_type / total_events * 100), 2) if total_events > 0 else 0,
                'students_with_branch': students_with_branch,
                'branch_coverage': round((students_with_branch / total_students * 100), 2) if total_students > 0 else 0,
                'students_with_year': students_with_year,
                'year_coverage': round((students_with_year / total_students * 100), 2) if total_students > 0 else 0,
            }
        }
    
    def get_scan_source_distribution(self) -> dict:
        """
        Analyze distribution of scan sources
        
        Returns:
            dict: Breakdown of scan sources
        """
        scan_distribution = self.db.query(
            models.Attendance.scan_source,
            func.count(models.Attendance.id).label('count')
        ).group_by(models.Attendance.scan_source).all()
        
        total = sum([d.count for d in scan_distribution])
        
        return {
            'total_scans': total,
            'by_source': {
                str(d.scan_source): {
                    'count': d.count,
                    'percentage': round((d.count / total * 100), 2) if total > 0 else 0
                }
                for d in scan_distribution
            }
        }
    
    def run_full_validation(self) -> dict:
        """
        Run all validation checks and return comprehensive report
        
        Returns:
            dict: Complete data quality assessment
        """
        return {
            'timestamp': datetime.now().isoformat(),
            'statistics': self.get_data_statistics(),
            'duplicates': self.check_duplicate_scans(),
            'orphaned_records': self.check_orphaned_attendance(),
            'scan_sources': self.get_scan_source_distribution(),
            'overall_status': self._calculate_overall_status()
        }
    
    def _calculate_overall_status(self) -> dict:
        """Calculate overall AI readiness status"""
        stats = self.get_data_statistics()
        duplicates = self.check_duplicate_scans()
        orphaned = self.check_orphaned_attendance()
        
        # Calculate readiness score (0-100)
        score = 100
        issues = []
        
        # Deduct for orphaned records
        if orphaned['orphaned_count'] > 0:
            score -= 20
            issues.append(f"{orphaned['orphaned_count']} orphaned records need cleanup")
        
        # Deduct for duplicates
        if duplicates['duplicate_count'] > 0:
            score -= 10
            issues.append(f"{duplicates['duplicate_count']} duplicate scans detected")
        
        # Deduct for missing AI fields
        ai_readiness = stats['ai_readiness']
        if ai_readiness['capacity_coverage'] < 50:
            score -= 15
            issues.append(f"Only {ai_readiness['capacity_coverage']}% events have capacity data")
        
        if ai_readiness['type_coverage'] < 50:
            score -= 15
            issues.append(f"Only {ai_readiness['type_coverage']}% events have type data")
        
        # Determine status
        if score >= 90:
            status = "EXCELLENT"
        elif score >= 70:
            status = "GOOD"
        elif score >= 50:
            status = "FAIR"
        else:
            status = "NEEDS_IMPROVEMENT"
        
        return {
            'score': max(0, score),
            'status': status,
            'issues': issues,
            'ready_for_ai': score >= 70
        }
