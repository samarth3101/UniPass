"""
Automatically push missing organizer and scanner certificates for Event 58
"""
from app.db.database import SessionLocal
from app.services.role_certificate_service import (
    issue_organizer_certificates,
    issue_scanner_certificates
)

db = SessionLocal()
event_id = 58

print("\n" + "="*70)
print("PUSHING MISSING CERTIFICATES FOR EVENT 58")
print("="*70 + "\n")

# Push organizer certificates
print("📋 Pushing ORGANIZER certificates...")
org_result = issue_organizer_certificates(db, event_id)
print(f"   Result: {org_result}")

if org_result.get('success'):
    issued = org_result.get('issued', 0)
    emailed = org_result.get('emailed', 0)
    failed = org_result.get('failed', 0)
    
    if issued > 0:
        if emailed > 0:
            print(f"   ✅ SUCCESS: {issued} certificate(s) created, {emailed} email(s) sent")
        else:
            print(f"   ⚠️  PARTIAL: {issued} certificate(s) created but {failed} email(s) failed")
    else:
        print(f"   ℹ️  INFO: {org_result.get('message', 'No action taken')}")
else:
    print(f"   ❌ ERROR: {org_result.get('error', 'Unknown error')}")

print()

# Push scanner certificates
print("📱 Pushing SCANNER certificates...")
scan_result = issue_scanner_certificates(db, event_id)
print(f"   Result: {scan_result}")

if scan_result.get('success'):
    issued = scan_result.get('issued', 0)
    emailed = scan_result.get('emailed', 0)
    failed = scan_result.get('failed', 0)
    
    if issued > 0:
        if emailed > 0:
            print(f"   ✅ SUCCESS: {issued} certificate(s) created, {emailed} email(s) sent")
        else:
            print(f"   ⚠️  PARTIAL: {issued} certificate(s) created but {failed} email(s) failed")
    else:
        print(f"   ℹ️  INFO: {scan_result.get('message', 'No action taken')}")
else:
    print(f"   ❌ ERROR: {scan_result.get('error', 'Unknown error')}")

print("\n" + "="*70)
print("FINAL STATUS")
print("="*70 + "\n")

# Show final certificate status
from app.models.certificate import Certificate

certs = db.query(Certificate).filter(Certificate.event_id == event_id).all()

print(f"Total certificates for Event 58: {len(certs)}\n")

for cert in certs:
    role = (cert.role_type or 'unknown').upper()
    recipient = cert.recipient_name or cert.student_prn or "Unknown"
    status = "✅ SENT" if cert.email_sent else "❌ FAILED"
    print(f"   {status} | {role:12} | {recipient}")

sent_count = sum(1 for c in certs if c.email_sent)
failed_count = len(certs) - sent_count

print(f"\n{'='*70}")
print(f"SUMMARY: {sent_count} sent successfully, {failed_count} failed")
print(f"{'='*70}\n")

if failed_count > 0:
    print("⚠️  Some emails failed to send (likely SMTP timeout)")
    print("   Certificates were created successfully in the database")
    print("   Use 'Resend Failed' button to retry sending emails\n")

db.close()
