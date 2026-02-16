"""
Test the conflict detection fix for Event 58
"""
from app.db.database import SessionLocal
from app.services.reconciliation_service import ReconciliationService
from app.models.certificate import Certificate

db = SessionLocal()

print("\n" + "=" * 70)
print("TEST: Conflict Detection for Event 58")
print("=" * 70 + "\n")

event_id = 58

# Check certificates for this event
print("1. Checking certificates...")
certs = db.query(Certificate).filter(Certificate.event_id == event_id).all()
print(f"   Total certificates: {len(certs)}")

student_certs = [c for c in certs if c.student_prn]
non_student_certs = [c for c in certs if not c.student_prn]

print(f"   Student certificates (with PRN): {len(student_certs)}")
print(f"   Non-student certificates (organizer/scanner/volunteer): {len(non_student_certs)}")

if non_student_certs:
    print("\n   Non-student certificates:")
    for cert in non_student_certs:
        role = (cert.role_type or 'unknown').upper()
        recipient = cert.recipient_name or cert.recipient_email or 'Unknown'
        print(f"   - {role}: {recipient}")

# Test the conflict detection service
print("\n2. Testing conflict detection service...")
service = ReconciliationService(db)

try:
    conflicts = service.get_event_conflicts(event_id)
    print(f"   ✓ Conflicts detected: {len(conflicts)}")
    
    if conflicts:
        print("\n   Conflict details:")
        for conflict in conflicts[:5]:  # Show first 5
            prn = conflict.get('student_prn', 'Unknown')
            status = conflict.get('canonical_status', 'Unknown')
            num_conflicts = len(conflict.get('conflicts', []))
            print(f"   - PRN: {prn}")
            print(f"     Status: {status}")
            print(f"     Issues: {num_conflicts}")
        
        if len(conflicts) > 5:
            print(f"   ... and {len(conflicts) - 5} more")
    else:
        print("   No conflicts found for this event")
    
    print("\n   ✓ Test passed - no errors!")
    
except Exception as e:
    print(f"\n   ✗ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("TEST COMPLETED")
print("=" * 70 + "\n")

db.close()
