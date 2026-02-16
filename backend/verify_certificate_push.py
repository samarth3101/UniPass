"""
Verify what will happen when pushing organizer/scanner certificates again
"""
from app.db.database import SessionLocal
from app.models.certificate import Certificate
from app.models.event import Event
from app.models.user import User
from app.models.attendance import Attendance

db = SessionLocal()

event_id = 58
event = db.query(Event).filter(Event.id == event_id).first()

print(f"\n{'='*70}")
print(f"Event #{event_id}: {event.title if event else 'Not Found'}")
print(f"{'='*70}\n")

if not event:
    print("Event not found!")
    db.close()
    exit(1)

# Check organizer
print("📋 ORGANIZER ROLE:")
print("-" * 70)
creator = db.query(User).filter(User.id == event.created_by).first()
if creator:
    print(f"   Organizer: {creator.full_name or creator.email}")
    print(f"   Email: {creator.email}")
    
    existing_org_cert = db.query(Certificate).filter(
        Certificate.event_id == event_id,
        Certificate.role_type == 'organizer',
        Certificate.recipient_email == creator.email
    ).first()
    
    if existing_org_cert:
        print(f"   Status: ✅ Certificate ALREADY EXISTS (ID: {existing_org_cert.certificate_id})")
        print(f"   Action: Will be SKIPPED (duplicate prevention)")
    else:
        print(f"   Status: ❌ NO CERTIFICATE")
        print(f"   Action: Will be CREATED when pushed")
else:
    print("   No organizer found")

# Check scanners
print(f"\n📱 SCANNER ROLE:")
print("-" * 70)
scanner_ids = db.query(Attendance.scanner_id).filter(
    Attendance.event_id == event_id,
    Attendance.scanner_id.isnot(None)
).distinct().all()

if scanner_ids:
    scanner_ids = [sid[0] for sid in scanner_ids]
    print(f"   Found {len(scanner_ids)} scanner(s)\n")
    
    for scanner_id in scanner_ids:
        scanner = db.query(User).filter(User.id == scanner_id).first()
        if scanner:
            print(f"   Scanner: {scanner.full_name or scanner.email}")
            print(f"   Email: {scanner.email}")
            
            existing_scan_cert = db.query(Certificate).filter(
                Certificate.event_id == event_id,
                Certificate.role_type == 'scanner',
                Certificate.recipient_email == scanner.email
            ).first()
            
            if existing_scan_cert:
                print(f"   Status: ✅ Certificate ALREADY EXISTS (ID: {existing_scan_cert.certificate_id})")
                print(f"   Action: Will be SKIPPED (duplicate prevention)\n")
            else:
                print(f"   Status: ❌ NO CERTIFICATE")
                print(f"   Action: Will be CREATED when pushed\n")
else:
    print("   No scanners found")

# Check existing certificates
print(f"📜 EXISTING CERTIFICATES:")
print("-" * 70)
existing_certs = db.query(Certificate).filter(Certificate.event_id == event_id).all()

if existing_certs:
    for cert in existing_certs:
        role = (cert.role_type or 'unknown').upper()
        recipient = cert.recipient_name or cert.student_prn or "Unknown"
        status = "✅ SENT" if cert.email_sent else "❌ FAILED"
        print(f"   {role:12} | {status} | {recipient}")
else:
    print("   No existing certificates")

print(f"\n{'='*70}")
print("RECOMMENDATION:")
print("   1. Open Certificate Push Modal for Event 58")
print("   2. Select ONLY 'Organizer' and 'Scanner' roles")
print("   3. Click 'Send Certificates'")
print("   4. Duplicate prevention will skip existing certificates")
print("   5. New certificates will be created for missing roles")
print(f"{'='*70}\n")

db.close()
