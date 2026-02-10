from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import timedelta, datetime
from typing import Optional
import pandas as pd

from app.models.attendance import Attendance
from app.models.event import Event
from app.models.student import Student


class DescriptiveAnalyticsService:
    """
    Phase 1: Descriptive Analytics
    Converts raw attendance data into actionable insights.
    No machine learning in this phase - pure statistical analysis.
    """

    def __init__(self, db: Session):
        self.db = db
        
    def get_event_attendance_distribution(self, event_id: int) -> dict:
        """
        Analyze attendance timing behavior for a single event
        """

        event = self.db.query(Event).filter(Event.id == event_id).first()
        if not event:
            return {"error": "Event not found"}

        attendance = self.db.query(Attendance).filter(
            Attendance.event_id == event_id
        ).all()

        if not attendance:
            return {
                "event_id": event_id,
                "event_title": event.title,
                "total_attendance": 0,
                "message": "No attendance data"
            }

        event_start = event.start_time

        rows = []
        for a in attendance:
            rows.append({
                "student_prn": a.student_prn,
                "scanned_at": a.scanned_at,
                "minutes_after_start": (
                    (a.scanned_at - event_start).total_seconds() / 60
                )
            })

        df = pd.DataFrame(rows)

        early = df[df["minutes_after_start"] < -5]
        on_time = df[
            (df["minutes_after_start"] >= -5) &
            (df["minutes_after_start"] <= 10)
        ]
        late = df[df["minutes_after_start"] > 10]

        return {
            "event_id": event.id,
            "event_title": event.title,
            "event_type": event.event_type,
            "capacity": event.capacity,
            "total_attendance": len(df),
            "attendance_rate": round(
                (len(df) / event.capacity) * 100, 2
            ) if event.capacity else None,
            "temporal_distribution": {
                "early": len(early),
                "on_time": len(on_time),
                "late": len(late)
            },
            "scan_window": {
                "first_scan": df["scanned_at"].min().isoformat() if not df.empty else None,
                "last_scan": df["scanned_at"].max().isoformat() if not df.empty else None,
                "duration_minutes": round(
                    (df["scanned_at"].max() - df["scanned_at"].min()).total_seconds() / 60,
                    2
                ) if not df.empty else 0
            },
            "peak_scan_time": df["scanned_at"].mode()[0].isoformat() if not df.empty and not df["scanned_at"].mode().empty else None
        }
    
    def get_student_attendance_consistency(self, student_prn: str) -> dict:
        """
        Analyze individual student attendance patterns
        """
        attendance_count = self.db.query(func.count(Attendance.id))\
            .filter(Attendance.student_prn == student_prn)\
            .scalar()
        
        if not attendance_count:
            return {
                "student_prn": student_prn,
                "total_attended": 0,
                "message": "No attendance records found"
            }
        
        total_events = self.db.query(func.count(Event.id)).scalar()
        
        # Get student details
        student = self.db.query(Student).filter(Student.prn == student_prn).first()
        
        # Get attendance by event type
        attendance_by_type = self.db.query(
            Event.event_type,
            func.count(Attendance.id).label('count')
        ).join(Attendance, Event.id == Attendance.event_id)\
         .filter(Attendance.student_prn == student_prn)\
         .group_by(Event.event_type)\
         .all()
        
        # Late arrival analysis
        late_arrivals = self.db.query(Attendance)\
            .join(Event, Attendance.event_id == Event.id)\
            .filter(
                Attendance.student_prn == student_prn,
                Attendance.scanned_at >= Event.start_time + timedelta(minutes=10)
            ).count()
        
        return {
            "student_prn": student_prn,
            "student_name": student.name if student else None,
            "branch": student.branch if student else None,
            "year": student.year if student else None,
            "total_attended": attendance_count,
            "total_events": total_events,
            "attendance_rate": round((attendance_count / total_events * 100), 2) if total_events > 0 else 0,
            "by_event_type": {item.event_type: item.count for item in attendance_by_type} if attendance_by_type else {},
            "punctuality": {
                "late_count": late_arrivals,
                "late_percentage": round((late_arrivals / attendance_count * 100), 2) if attendance_count > 0 else 0,
                "on_time_count": attendance_count - late_arrivals
            }
        }
    
    def get_department_participation(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> dict:
        """
        Department-wise participation analysis
        """
        # Use UPPER and TRIM to normalize branch names (handles typos and case differences)
        normalized_branch = func.upper(func.trim(Student.branch))
        
        # Base query for attendance stats by department
        query = self.db.query(
            normalized_branch.label('branch'),
            func.count(func.distinct(Attendance.student_prn)).label('active_students'),
            func.count(Attendance.id).label('total_attendance')
        ).join(Attendance, Student.prn == Attendance.student_prn)\
         .join(Event, Attendance.event_id == Event.id)\
         .filter(Student.branch != None)
        
        # Apply date filters if provided
        if start_date:
            query = query.filter(Event.start_time >= start_date)
        if end_date:
            query = query.filter(Event.start_time <= end_date)
        
        dept_stats = query.group_by(normalized_branch).all()
        
        # Get total students by department (also normalized)
        total_students_by_dept = self.db.query(
            normalized_branch.label('branch'),
            func.count(Student.prn).label('total')
        ).filter(Student.branch != None)\
         .group_by(normalized_branch)\
         .all()
        
        dept_dict = {d.branch: d.total for d in total_students_by_dept}
        
        departments = []
        for stat in dept_stats:
            total = dept_dict.get(stat.branch, 0)
            departments.append({
                "branch": stat.branch,
                "active_students": stat.active_students,
                "total_students": total,
                "participation_rate": round((stat.active_students / total * 100), 2) if total > 0 else 0,
                "total_attendance": stat.total_attendance,
                "avg_events_per_student": round(stat.total_attendance / stat.active_students, 2) if stat.active_students > 0 else 0
            })
        
        # Sort by total attendance descending
        departments.sort(key=lambda x: x['total_attendance'], reverse=True)
        
        return {
            "departments": departments,
            "total_departments": len(departments)
        }
    
    def get_time_pattern_analysis(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> dict:
        """
        Analyze best times for events based on attendance
        """
        query = self.db.query(
            Event.id,
            Event.start_time,
            Event.capacity,
            func.count(Attendance.id).label('attendance')
        ).join(Attendance, Event.id == Attendance.event_id)\
         .filter(Event.start_time != None)
        
        # Apply date filters if provided
        if start_date:
            query = query.filter(Event.start_time >= start_date)
        if end_date:
            query = query.filter(Event.start_time <= end_date)
        
        events_with_attendance = query.group_by(Event.id, Event.start_time, Event.capacity).all()
        
        if not events_with_attendance:
            return {
                "message": "No events with attendance data found",
                "by_hour": {},
                "by_day": {},
                "best_time": None
            }
        
        rows = []
        for e in events_with_attendance:
            rows.append({
                "event_id": e.id,
                "hour": e.start_time.hour,
                "day_of_week": e.start_time.strftime('%A'),
                "attendance": e.attendance,
                "capacity": e.capacity,
                "attendance_rate": (e.attendance / e.capacity * 100) if e.capacity else None
            })
        
        df = pd.DataFrame(rows)
        
        # Calculate averages
        by_hour = df.groupby('hour')['attendance'].mean().round(2).to_dict()
        by_day = df.groupby('day_of_week')['attendance'].mean().round(2).to_dict()
        
        # Find best times
        best_hour = df.groupby('hour')['attendance'].mean().idxmax() if not df.empty else None
        best_day = df.groupby('day_of_week')['attendance'].mean().idxmax() if not df.empty else None
        
        # Calculate attendance rate by time if capacity data available
        by_hour_rate = {}
        by_day_rate = {}
        
        if 'attendance_rate' in df.columns and df['attendance_rate'].notna().any():
            by_hour_rate = df.groupby('hour')['attendance_rate'].mean().round(2).to_dict()
            by_day_rate = df.groupby('day_of_week')['attendance_rate'].mean().round(2).to_dict()
        
        return {
            "by_hour": {str(k): v for k, v in by_hour.items()},
            "by_day": by_day,
            "by_hour_rate": {str(k): v for k, v in by_hour_rate.items()} if by_hour_rate else {},
            "by_day_rate": by_day_rate if by_day_rate else {},
            "best_time": {
                "hour": int(best_hour) if best_hour is not None else None,
                "day": best_day,
                "avg_attendance": round(df.groupby('hour')['attendance'].mean().max(), 2) if best_hour is not None else None
            },
            "total_events_analyzed": len(events_with_attendance)
        }
    
    def get_overall_summary(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> dict:
        """
        Get overall system statistics summary
        """
        # Base queries
        event_query = self.db.query(func.count(Event.id))
        attendance_query = self.db.query(func.count(Attendance.id))
        attendance_event_query = self.db.query(func.count(func.distinct(Attendance.event_id)))
        
        # Apply date filters if provided
        if start_date or end_date:
            if start_date:
                event_query = event_query.filter(Event.start_time >= start_date)
                attendance_query = attendance_query.join(Event, Attendance.event_id == Event.id).filter(Event.start_time >= start_date)
                attendance_event_query = attendance_event_query.join(Event, Attendance.event_id == Event.id).filter(Event.start_time >= start_date)
            if end_date:
                event_query = event_query.filter(Event.start_time <= end_date)
                if not start_date:
                    attendance_query = attendance_query.join(Event, Attendance.event_id == Event.id)
                    attendance_event_query = attendance_event_query.join(Event, Attendance.event_id == Event.id)
                attendance_query = attendance_query.filter(Event.start_time <= end_date)
                attendance_event_query = attendance_event_query.filter(Event.start_time <= end_date)
        
        total_events = event_query.scalar()
        total_students = self.db.query(func.count(Student.prn)).scalar()
        total_attendance = attendance_query.scalar()
        
        # Events with attendance
        events_with_attendance = attendance_event_query.scalar()
        
        # Active students (with at least one attendance)
        active_students = self.db.query(
            func.count(func.distinct(Attendance.student_prn))
        ).scalar()
        
        # Average attendance per event
        avg_attendance = total_attendance / events_with_attendance if events_with_attendance > 0 else 0
        
        # Get date range
        date_range = self.db.query(
            func.min(Event.start_time).label('first'),
            func.max(Event.start_time).label('last')
        ).first()
        
        return {
            "summary": {
                "total_events": total_events,
                "events_with_attendance": events_with_attendance,
                "total_students": total_students,
                "active_students": active_students,
                "student_engagement_rate": round((active_students / total_students * 100), 2) if total_students > 0 else 0,
                "total_attendance_records": total_attendance,
                "avg_attendance_per_event": round(avg_attendance, 2)
            },
            "date_range": {
                "first_event": date_range.first.isoformat() if date_range.first else None,
                "last_event": date_range.last.isoformat() if date_range.last else None,
                "span_days": (date_range.last - date_range.first).days if date_range.first and date_range.last else 0
            }
        }