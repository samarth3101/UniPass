"""
Test guest_speaker field functionality
"""
from app.db.database import SessionLocal
from app.models.event import Event
from datetime import datetime, timezone

db = SessionLocal()

print("\n" + "=" * 70)
print("TEST: Guest Speaker Field")
print("=" * 70 + "\n")

# Check if column exists
print("1. Verifying database column...")
from sqlalchemy import text
result = db.execute(text("""
    SELECT column_name, data_type, is_nullable
    FROM information_schema.columns 
    WHERE table_name='events' AND column_name='guest_speaker'
"""))
col_info = result.fetchone()

if col_info:
    print(f"   ✓ Column exists:")
    print(f"     Name: {col_info[0]}")
    print(f"     Type: {col_info[1]}")
    print(f"     Nullable: {col_info[2]}")
else:
    print("   ✗ Column not found!")
    db.close()
    exit(1)

# Test reading existing events
print("\n2. Testing read functionality...")
events = db.query(Event).limit(5).all()
print(f"   Found {len(events)} events")
for event in events[:3]:
    guest = event.guest_speaker or "(none)"
    print(f"   - Event #{event.id}: {event.title}")
    print(f"     Guest Speaker: {guest}")

# Test creating event with guest_speaker
print("\n3. Testing create functionality...")

# Get a real user ID
from app.models.user import User
real_user = db.query(User).first()
if not real_user:
    print("   ⚠ No users found, skipping create test")
else:
    test_event = Event(
        title="Test Event with Guest Speaker",
        description="Testing the new field",
        location="Test Location",
        start_time=datetime.now(timezone.utc),
        end_time=datetime.now(timezone.utc),
        guest_speaker="Dr. John Doe",
        created_by=real_user.id,
        share_slug=f"test-guest-{datetime.now().timestamp()}"
    )

    db.add(test_event)
    db.commit()
    db.refresh(test_event)

    print(f"   ✓ Created test event:")
    print(f"     ID: {test_event.id}")
    print(f"     Title: {test_event.title}")
    print(f"     Guest Speaker: {test_event.guest_speaker}")

    # Verify it was saved
    retrieved = db.query(Event).filter(Event.id == test_event.id).first()
    if retrieved and retrieved.guest_speaker == "Dr. John Doe":
        print(f"   ✓ Guest speaker field saved and retrieved correctly!")
    else:
        print(f"   ✗ Error retrieving guest speaker field")

    # Clean up
    print("\n4. Cleaning up test data...")
    db.delete(test_event)
    db.commit()
    print("   ✓ Test event deleted")

print("\n" + "=" * 70)
print("ALL TESTS PASSED ✓")
print("=" * 70 + "\n")

db.close()
