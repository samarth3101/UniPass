"""Test Phase 1 Analytics Endpoints"""
from app.db.database import SessionLocal
from app.services.analytics_service import DescriptiveAnalyticsService

db = SessionLocal()
service = DescriptiveAnalyticsService(db)

print("="*70)
print("PHASE 1 - DESCRIPTIVE ANALYTICS - ENDPOINT TESTS")
print("="*70)

# Test 1: Overall Summary
print("\n1. Testing Overall Summary...")
try:
    summary = service.get_overall_summary()
    print(f"✅ Total Events: {summary['summary']['total_events']}")
    print(f"✅ Total Students: {summary['summary']['total_students']}")
    print(f"✅ Engagement Rate: {summary['summary']['student_engagement_rate']}%")
    print(f"✅ Avg Attendance/Event: {summary['summary']['avg_attendance_per_event']}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 2: Event Distribution
print("\n2. Testing Event Attendance Distribution (Event ID 1)...")
try:
    dist = service.get_event_attendance_distribution(1)
    if "error" not in dist:
        print(f"✅ Event: {dist['event_title']}")
        print(f"✅ Total Attendance: {dist['total_attendance']}")
        print(f"✅ Attendance Rate: {dist['attendance_rate']}%" if dist['attendance_rate'] else "✅ Attendance Rate: N/A")
        print(f"✅ Temporal: Early={dist['temporal_distribution']['early']}, On-time={dist['temporal_distribution']['on_time']}, Late={dist['temporal_distribution']['late']}")
    else:
        print(f"⚠️  {dist['error']}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 3: Department Participation
print("\n3. Testing Department Participation...")
try:
    depts = service.get_department_participation()
    print(f"✅ Total Departments: {depts['total_departments']}")
    for dept in depts['departments'][:3]:  # Show first 3
        print(f"   • {dept['branch']}: {dept['participation_rate']}% participation " +
              f"({dept['active_students']}/{dept['total_students']} students)")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 4: Time Pattern Analysis
print("\n4. Testing Time Pattern Analysis...")
try:
    patterns = service.get_time_pattern_analysis()
    if "message" not in patterns:
        print(f"✅ Events Analyzed: {patterns['total_events_analyzed']}")
        if patterns['best_time']['hour'] is not None:
            print(f"✅ Best Hour: {patterns['best_time']['hour']}:00")
            print(f"✅ Best Day: {patterns['best_time']['day']}")
            print(f"✅ Avg Attendance: {patterns['best_time']['avg_attendance']}")
        else:
            print("⚠️  Not enough data for best time analysis")
    else:
        print(f"⚠️  {patterns['message']}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 5: Student Consistency (using first student)
print("\n5. Testing Student Attendance Consistency...")
try:
    # Get a sample student PRN
    from app.models.student import Student
    sample_student = db.query(Student).first()
    if sample_student:
        consistency = service.get_student_attendance_consistency(sample_student.prn)
        if "message" not in consistency:
            print(f"✅ Student: {consistency['student_name']} ({consistency['student_prn']})")
            print(f"✅ Total Attended: {consistency['total_attended']}/{consistency['total_events']}")
            print(f"✅ Attendance Rate: {consistency['attendance_rate']}%")
            print(f"✅ Late Count: {consistency['punctuality']['late_count']} ({consistency['punctuality']['late_percentage']}%)")
        else:
            print(f"⚠️  {consistency['message']}")
    else:
        print("⚠️  No students found in database")
except Exception as e:
    print(f"❌ Error: {e}")

db.close()
print("\n" + "="*70)
print("✅ ALL ANALYTICS TESTS COMPLETED!")
print("="*70)
