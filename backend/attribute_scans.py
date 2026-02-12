#!/usr/bin/env python3
"""
Helper script to attribute existing scans to scanner operators
Run this if you need to assign old scans (with NULL scanner_id) to specific scanners
"""
import sys
sys.path.append('/Users/samarthpatil/Desktop/UniPass/backend')

from sqlalchemy import func
from app.db.database import SessionLocal
from app.models.attendance import Attendance
from app.models.user import User, UserRole

db = SessionLocal()

# Check how many scans have NULL scanner_id
null_scans = db.query(func.count(Attendance.id)).filter(
    Attendance.scanner_id == None
).scalar()

print(f"\n📊 Scanner Attribution Report")
print("=" * 60)
print(f"Total scans with NULL scanner_id: {null_scans}")

if null_scans == 0:
    print("✅ All scans are already attributed to scanners!")
    db.close()
    sys.exit(0)

# Get all scanners
scanners = db.query(User).filter(User.role == UserRole.SCANNER).all()

if not scanners:
    print("\n⚠️  No scanner operators found in the system.")
    db.close()
    sys.exit(0)

print(f"\nFound {len(scanners)} scanner operator(s):")
for idx, scanner in enumerate(scanners, 1):
    print(f"  {idx}. {scanner.full_name or scanner.email} ({scanner.email})")

print("\n" + "=" * 60)
print("Options:")
print("  1. Attribute all untracked scans to first scanner")
print("  2. Attribute to specific scanner (enter number)")
print("  3. Leave as-is (future scans will be tracked)")
print("=" * 60)

choice = input("\nYour choice (1/2/3): ").strip()

if choice == "3":
    print("\n✅ No changes made. Future scans will be properly tracked.")
    db.close()
    sys.exit(0)

scanner_to_use = None

if choice == "1":
    scanner_to_use = scanners[0]
elif choice == "2":
    try:
        scanner_idx = int(input(f"Enter scanner number (1-{len(scanners)}): ")) - 1
        if 0 <= scanner_idx < len(scanners):
            scanner_to_use = scanners[scanner_idx]
        else:
            print("❌ Invalid scanner number")
            db.close()
            sys.exit(1)
    except ValueError:
        print("❌ Invalid input")
        db.close()
        sys.exit(1)
else:
    print("❌ Invalid choice")
    db.close()
    sys.exit(1)

# Update the scans
print(f"\n🔄 Attributing {null_scans} scans to {scanner_to_use.full_name or scanner_to_use.email}...")

db.query(Attendance).filter(
    Attendance.scanner_id == None
).update({
    "scanner_id": scanner_to_use.id,
    "scan_source": "qr_scan"  # Set source for old records
})

db.commit()

print(f"✅ Successfully attributed {null_scans} scans!")

# Show updated counts
print("\n📊 Updated Scanner Statistics:")
print("=" * 60)

for scanner in scanners:
    count = db.query(func.count(Attendance.id)).filter(
        Attendance.scanner_id == scanner.id
    ).scalar()
    print(f"  {scanner.full_name or scanner.email}: {count} scans")

db.close()
print("\n✅ Done!\n")
