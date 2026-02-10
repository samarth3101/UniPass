"""
Database Migration: AI Phase 0 - Add Fields

This migration adds AI readiness fields to Event and Attendance tables:
- Event: event_type, capacity, department
- Attendance: scan_source, scanner_id, device_info

Run this script from the backend directory:
    python migrate_ai_phase0_fields.py
"""

import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

def migrate():
    """Add AI Phase 0 fields to Event and Attendance tables"""
    print("🔄 Starting migration: AI Phase 0 - Add Fields")
    print(f"📍 Database URL: {settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else settings.DATABASE_URL}")
    
    try:
        engine = create_engine(settings.DATABASE_URL)
        from sqlalchemy import inspect
        inspector = inspect(engine)
        
        # Check Event table columns
        event_columns = [col['name'] for col in inspector.get_columns('events')]
        attendance_columns = [col['name'] for col in inspector.get_columns('attendance')]
        
        print(f"\n📊 Current Event columns: {', '.join(event_columns)}")
        print(f"📊 Current Attendance columns: {', '.join(attendance_columns)}")
        
        with engine.connect() as conn:
            # Add Event fields
            print("\n🔧 Updating events table...")
            
            if 'event_type' not in event_columns:
                conn.execute(text("ALTER TABLE events ADD COLUMN event_type VARCHAR"))
                conn.commit()
                print("  ✅ Added event_type column")
            else:
                print("  ⏭️  event_type already exists")
            
            if 'capacity' not in event_columns:
                conn.execute(text("ALTER TABLE events ADD COLUMN capacity INTEGER"))
                conn.commit()
                print("  ✅ Added capacity column")
            else:
                print("  ⏭️  capacity already exists")
            
            if 'department' not in event_columns:
                conn.execute(text("ALTER TABLE events ADD COLUMN department VARCHAR"))
                conn.commit()
                print("  ✅ Added department column")
            else:
                print("  ⏭️  department already exists")
            
            # Add Attendance fields
            print("\n🔧 Updating attendance table...")
            
            if 'scan_source' not in attendance_columns:
                # Create enum type if it doesn't exist
                conn.execute(text("""
                    DO $$ BEGIN
                        CREATE TYPE scansource AS ENUM ('qr_scan', 'admin_override', 'bulk_upload', 'api_integration');
                    EXCEPTION
                        WHEN duplicate_object THEN null;
                    END $$;
                """))
                conn.commit()
                
                conn.execute(text("ALTER TABLE attendance ADD COLUMN scan_source scansource DEFAULT 'qr_scan' NOT NULL"))
                conn.commit()
                print("  ✅ Added scan_source column with enum type")
            else:
                print("  ⏭️  scan_source already exists")
            
            if 'scanner_id' not in attendance_columns:
                conn.execute(text("ALTER TABLE attendance ADD COLUMN scanner_id INTEGER REFERENCES users(id)"))
                conn.commit()
                print("  ✅ Added scanner_id column")
            else:
                print("  ⏭️  scanner_id already exists")
            
            if 'device_info' not in attendance_columns:
                conn.execute(text("ALTER TABLE attendance ADD COLUMN device_info VARCHAR"))
                conn.commit()
                print("  ✅ Added device_info column")
            else:
                print("  ⏭️  device_info already exists")
        
        # Verify changes
        print("\n🔍 Verifying migration...")
        inspector = inspect(engine)
        new_event_columns = [col['name'] for col in inspector.get_columns('events')]
        new_attendance_columns = [col['name'] for col in inspector.get_columns('attendance')]
        
        print(f"\n✅ Events table now has {len(new_event_columns)} columns:")
        print(f"   {', '.join(new_event_columns)}")
        print(f"\n✅ Attendance table now has {len(new_attendance_columns)} columns:")
        print(f"   {', '.join(new_attendance_columns)}")
        
        print("\n" + "="*60)
        print("✅ Migration completed successfully!")
        print("="*60)
        print("\n📋 AI Readiness Phase 0 - Fields Added:")
        print("   Event Table:")
        print("     • event_type - categorize events (workshop, seminar, etc.)")
        print("     • capacity - max attendees for attendance rate calculations")
        print("     • department - department organizing event (CS, IT, etc.)")
        print("\n   Attendance Table:")
        print("     • scan_source - track how attendance was recorded")
        print("     • scanner_id - who performed the scan")
        print("     • device_info - browser/device fingerprint")
        print("\n💡 Next step: Run migrate_ai_phase0_indexes.py to add AI-optimized indexes")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Migration failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = migrate()
    sys.exit(0 if success else 1)
