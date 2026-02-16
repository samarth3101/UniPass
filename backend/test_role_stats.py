"""
Test role-stats endpoint calculation for Event 58
"""
from app.db.database import SessionLocal
from app.models.event import Event
from app.models.user import User
from app.models.certificate import Certificate
from app.models.attendance import Attendance
from app.models.volunteer import Volunteer
from app.services.certificate_service import get_students_without_certificates

db = SessionLocal()
event_id = 58

print("\n" + "="*70)
print("ROLE STATS CALCULATION TEST - Event 58")
print("="*70 + "\n")

event = db.query(Event).filter(Event.id == event_id).first()

# ATTENDEES
print("📚 ATTENDEES:")
print("-" * 70)
students_without_certs = get_students_without_certificates(db, event_id)
attendee_count = len(students_without_certs)
print(f"   Students without certificates: {attendee_count}")
if students_without_certs:
    for student in students_without_certs[:5]:  # Show first 5
        print(f"   - {student.get('name')} ({student.get('prn')})")
    if len(students_without_certs) > 5:
        print(f"   ... and {len(students_without_certs) - 5} more")

# ORGANIZERS
print(f"\n📋 ORGANIZERS:")
print("-" * 70)
creator = db.query(User).filter(User.id == event.created_by).first()
if creator:
    print(f"   Event Creator: {creator.full_name or creator.email} ({creator.email})")
    
    organizer_cert = db.query(Certificate).filter(
        Certificate.event_id == event_id,
        Certificate.role_type == 'organizer',
        Certificate.recipient_email == creator.email
    ).first()
    
    if organizer_cert:
        print(f"   Status: ✅ Certificate exists (ID: {organizer_cert.certificate_id})")
        print(f"   Count: 0 (already has certificate)")
    else:
        print(f"   Status: ❌ No certificate")
        print(f"   Count: 1 (eligible)")
else:
    print("   No creator found")
    print("   Count: 0")

organizer_count = 0 if (creator and organizer_cert) else (1 if creator else 0)

# SCANNERS
print(f"\n📱 SCANNERS:")
print("-" * 70)
scanner_ids = db.query(Attendance.scanner_id).filter(
    Attendance.event_id == event_id,
    Attendance.scanner_id.isnot(None)
).distinct().all()

print(f"   Total unique scanners: {len(scanner_ids)}")
scanner_count = 0

for scanner_id_tuple in scanner_ids:
    scanner_id = scanner_id_tuple[0]
    scanner = db.query(User).filter(User.id == scanner_id).first()
    if scanner:
        print(f"   Scanner: {scanner.full_name or scanner.email} ({scanner.email})")
        
        scanner_cert = db.query(Certificate).filter(
            Certificate.event_id == event_id,
            Certificate.role_type == 'scanner',
            Certificate.recipient_email == scanner.email
        ).first()
        
        if scanner_cert:
            print(f"   Status: ✅ Certificate exists (ID: {scanner_cert.certificate_id})")
        else:
            print(f"   Status: ❌ No certificate")
            scanner_count += 1

print(f"   Count: {scanner_count} (eligible without certificates)")

# VOLUNTEERS
print(f"\n🤝 VOLUNTEERS:")
print("-" * 70)
volunteers = db.query(Volunteer).filter(Volunteer.event_id == event_id).all()
print(f"   Total volunteers: {len(volunteers)}")

volunteer_count = 0
for vol in volunteers:
    status = "✅ SENT" if vol.certificate_sent else "❌ NOT SENT"
    print(f"   {status} | {vol.name} ({vol.email})")
    if not vol.certificate_sent:
        volunteer_count += 1

print(f"   Count: {volunteer_count} (without certificates)")

# SUMMARY
print(f"\n{'='*70}")
print("API RESPONSE:")
print(f"{'='*70}")
print(f"""
{{
    "attendees": {attendee_count},
    "organizers": {organizer_count},
    "scanners": {scanner_count},
    "volunteers": {volunteer_count}
}}
""")
print(f"{'='*70}\n")

db.close()
