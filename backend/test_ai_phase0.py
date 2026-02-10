"""Test AI Phase 0 completion"""
from app.db.database import SessionLocal

# Import all models first to avoid circular dependency issues
from app.models import Event, Student, Attendance, User

# Now import the validator
from app.services.ai_data_validation import AIDataValidator

db = SessionLocal()
validator = AIDataValidator(db)

print("Testing AIDataValidator...")
report = validator.run_full_validation()

print("\n" + "="*70)
print("AI READINESS PHASE 0 - DATA QUALITY REPORT")
print("="*70)

print(f"\nOverall Score: {report['overall_status']['score']}/100")
print(f"Status: {report['overall_status']['status']}")
print(f"Ready for AI: {report['overall_status']['ready_for_ai']}")

if report['overall_status']['issues']:
    print("\nIssues Found:")
    for issue in report['overall_status']['issues']:
        print(f"  - {issue}")

print(f"\nStatistics:")
print(f"  Total Events: {report['statistics']['total_events']}")
print(f"  Total Students: {report['statistics']['total_students']}")
print(f"  Total Attendance: {report['statistics']['total_attendance']}")

print(f"\nAI Readiness:")
ai = report['statistics']['ai_readiness']
print(f"  Events with capacity: {ai['capacity_coverage']}%")
print(f"  Events with type: {ai['type_coverage']}%")
print(f"  Students with branch: {ai['branch_coverage']}%")

print(f"\nData Quality:")
print(f"  Duplicate scans: {report['duplicates']['duplicate_count']}")
print(f"  Orphaned records: {report['orphaned_records']['orphaned_count']}")

db.close()
print("\nAIDataValidator working correctly!")
