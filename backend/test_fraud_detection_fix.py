"""
Test fraud detection fix for Event 58
"""
from app.db.database import SessionLocal
from app.services.fraud_detection_service import FraudDetectionService
from app.models.certificate import Certificate

db = SessionLocal()

print("\n" + "=" * 70)
print("TEST: Fraud Detection for Event 58")
print("=" * 70 + "\n")

event_id = 58

# Show certificate breakdown
print("1. Certificate Breakdown:")
print("-" * 70)
all_certs = db.query(Certificate).filter(Certificate.event_id == event_id).all()
student_certs = [c for c in all_certs if c.student_prn]
role_certs = [c for c in all_certs if not c.student_prn]

print(f"   Total certificates: {len(all_certs)}")
print(f"   Student certificates (attendees): {len(student_certs)}")
for cert in student_certs:
    print(f"   - PRN: {cert.student_prn}, Role: {cert.role_type or 'attendee'}")

print(f"\n   Role-based certificates (non-students): {len(role_certs)}")
for cert in role_certs:
    role = (cert.role_type or 'unknown').upper()
    recipient = cert.recipient_name or cert.recipient_email
    print(f"   - {role}: {recipient}")

# Run fraud detection
print("\n2. Running Fraud Detection:")
print("-" * 70)
service = FraudDetectionService(db)

try:
    result = service.detect_fraud(event_id)
    
    print(f"   Scan completed at: {result['scanned_at']}")
    print(f"\n   Summary:")
    print(f"   - Total alerts: {result['summary']['total_alerts']}")
    print(f"   - High severity: {result['summary']['high_severity']}")
    print(f"   - Medium severity: {result['summary']['medium_severity']}")
    print(f"   - Low severity: {result['summary']['low_severity']}")
    
    if result['fraud_alerts']:
        print(f"\n   Fraud Alerts:")
        for i, alert in enumerate(result['fraud_alerts'], 1):
            print(f"\n   Alert #{i}:")
            print(f"   - Type: {alert['type']}")
            print(f"   - Severity: {alert['severity']}")
            print(f"   - Student PRN: {alert.get('student_prn', 'N/A')}")
            print(f"   - Description: {alert['description']}")
    else:
        print(f"\n   ✓ No fraud alerts detected!")
    
    print("\n   ✓ Test completed successfully!")
    
except Exception as e:
    print(f"\n   ✗ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("EXPECTED RESULT:")
print("- 0 fraud alerts (role-based certificates should be excluded)")
print("- Student certificates should be checked normally")
print("=" * 70 + "\n")

db.close()
