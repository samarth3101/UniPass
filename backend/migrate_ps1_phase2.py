#!/usr/bin/env python3
"""
PS1 Phase 2 Migration
Adds student_snapshots table for historical profile tracking
"""

import sys
sys.path.append('/Users/samarthpatil/Desktop/UniPass/backend')

from sqlalchemy import create_engine, text
from app.core.config import Settings

settings = Settings()

def run_migration():
    """Execute Phase 2 migration"""
    engine = create_engine(settings.DATABASE_URL)
    
    print("=" * 70)
    print("PS1 PHASE 2 MIGRATION - Student Snapshots")
    print("=" * 70)
    
    with engine.connect() as conn:
        # Create student_snapshots table
        print("\n1. Creating student_snapshots table...")
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS student_snapshots (
                id SERIAL PRIMARY KEY,
                student_prn VARCHAR NOT NULL,
                event_id INTEGER NOT NULL REFERENCES events(id) ON DELETE CASCADE,
                captured_at TIMESTAMP DEFAULT NOW() NOT NULL,
                snapshot_trigger VARCHAR NOT NULL,
                profile_data JSONB NOT NULL,
                participation_status JSONB,
                CONSTRAINT fk_snapshot_event FOREIGN KEY (event_id) REFERENCES events(id)
            );
        """))
        conn.commit()
        print("   ✅ student_snapshots table created")
        
        # Create indexes
        print("\n2. Creating indexes for student_snapshots...")
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS ix_student_snapshots_student_prn 
            ON student_snapshots(student_prn);
        """))
        conn.commit()
        print("   ✅ Index on student_prn created")
        
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS ix_student_snapshots_event_id 
            ON student_snapshots(event_id);
        """))
        conn.commit()
        print("   ✅ Index on event_id created")
        
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS ix_snapshot_student_event 
            ON student_snapshots(student_prn, event_id);
        """))
        conn.commit()
        print("   ✅ Composite index on (student_prn, event_id) created")
        
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS ix_snapshot_captured_at 
            ON student_snapshots(captured_at);
        """))
        conn.commit()
        print("   ✅ Index on captured_at created")
        
        # Verify table creation
        print("\n3. Verifying table creation...")
        result = conn.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'student_snapshots'
            );
        """))
        exists = result.scalar()
        
        if exists:
            print("   ✅ student_snapshots table: EXISTS")
        else:
            print("   ❌ student_snapshots table: MISSING")
            return False
        
        # Check indexes
        result = conn.execute(text("""
            SELECT indexname FROM pg_indexes 
            WHERE tablename = 'student_snapshots';
        """))
        indexes = [row[0] for row in result]
        print(f"   ✅ Indexes created: {len(indexes)}")
        for idx in indexes:
            print(f"      - {idx}")
        
        conn.commit()
    
    print("\n" + "=" * 70)
    print("✅ PS1 PHASE 2 MIGRATION COMPLETED SUCCESSFULLY!")
    print("=" * 70)
    print("\nNew Features Unlocked:")
    print("  📸 Student Snapshots - Historical profile tracking")
    print("  🕐 As-of queries - View profile at any point in time")
    print("  📊 Profile evolution - Compare snapshots over time")
    print("  🎯 Retroactive analysis - Audit historical data")
    print("\nAPI Endpoints Added:")
    print("  POST   /ps1/snapshots/{event_id}/capture")
    print("  GET    /ps1/snapshots/student/{prn}")
    print("  GET    /ps1/snapshots/student/{prn}/event/{event_id}")
    print("  GET    /ps1/snapshots/compare/{id1}/{id2}")
    print()
    
    return True

if __name__ == "__main__":
    try:
        success = run_migration()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Migration failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
