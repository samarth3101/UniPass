from app.db.database import SessionLocal
from app.models.certificate import Certificate

db = SessionLocal()
certs = db.query(Certificate).filter(Certificate.event_id == 58).all()

print(f"\n{'='*60}")
print(f"Event 58 - Certificate Status Report")
print(f"{'='*60}\n")

if not certs:
    print("No certificates found for this event")
else:
    print(f"Total Certificates: {len(certs)}\n")
    
    for cert in certs:
        status = "✓ SENT" if cert.email_sent else "✗ FAILED"
        role = (cert.role_type or "unknown").upper()
        recipient = cert.recipient_name or cert.student_prn or "Unknown"
        print(f"{status:10} | {role:12} | {recipient}")
    
    sent_count = sum(1 for c in certs if c.email_sent)
    failed_count = len(certs) - sent_count
    
    print(f"\n{'='*60}")
    print(f"Summary: {sent_count} sent successfully, {failed_count} failed/pending")
    print(f"{'='*60}\n")

db.close()
