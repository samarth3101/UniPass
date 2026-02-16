"""
Resend failed certificate emails for Event 58
"""
from app.db.database import SessionLocal
from app.models.certificate import Certificate
from app.models.event import Event
from app.services.email_service import send_certificate_email
from datetime import datetime, timezone

db = SessionLocal()
event_id = 58

print("\n" + "="*70)
print("RESENDING FAILED CERTIFICATE EMAILS FOR EVENT 58")
print("="*70 + "\n")

event = db.query(Event).filter(Event.id == event_id).first()

# Get failed certificates
failed_certs = db.query(Certificate).filter(
    Certificate.event_id == event_id,
    Certificate.email_sent == False
).all()

if not failed_certs:
    print("No failed certificates to resend!")
    db.close()
    exit(0)

print(f"Found {len(failed_certs)} certificate(s) with failed emails\n")

resent = 0
still_failed = 0

for cert in failed_certs:
    role = (cert.role_type or 'unknown').upper()
    recipient = cert.recipient_name or cert.student_prn
    email = cert.recipient_email or "unknown"
    
    print(f"📧 Attempting to resend: {role} - {recipient} ({email})")
    
    try:
        event_date = event.start_time.strftime('%B %d, %Y') if event.start_time else 'TBD'
        
        success = send_certificate_email(
            to_email=email,
            student_name=recipient,
            event_title=event.title,
            event_location=event.location or 'TBD',
            event_date=event_date,
            certificate_id=cert.certificate_id,
            role_type=cert.role_type or 'attendee'
        )
        
        if success:
            cert.email_sent = True
            cert.email_sent_at = datetime.now(timezone.utc)
            resent += 1
            print(f"   ✅ SUCCESS: Email sent!\n")
        else:
            still_failed += 1
            print(f"   ❌ FAILED: Email could not be sent (SMTP timeout)\n")
    
    except Exception as e:
        still_failed += 1
        print(f"   ❌ ERROR: {e}\n")

db.commit()

print("="*70)
print(f"RESULTS: {resent} resent successfully, {still_failed} still failed")
print("="*70 + "\n")

if still_failed > 0:
    print("⚠️  Email delivery is failing due to SMTP configuration/network issues")
    print("   Certificates ARE in the database and can be verified")
    print("   Consider using a different email service (SendGrid, Mailgun, etc.)\n")

# Show final status
print("FINAL CERTIFICATE STATUS:")
print("-" * 70)
all_certs = db.query(Certificate).filter(Certificate.event_id == event_id).all()
for cert in all_certs:
    role = (cert.role_type or 'unknown').upper()
    recipient = cert.recipient_name or cert.student_prn
    status = "✅ SENT" if cert.email_sent else "❌ FAILED"
    print(f"   {status} | {role:12} | {recipient}")

print()

db.close()
