#!/usr/bin/env python3
"""
Migration: Fix Audit Log Timestamps - Store as UTC with Timezone
"""
from datetime import datetime, timezone
from app.db.database import engine
from sqlalchemy import text

def migrate():
    print("🚀 Starting Audit Log Timestamp Migration...")
    print("=" * 70)
    
    with engine.connect() as conn:
        # Start transaction
        trans = conn.begin()
        
        try:
            # Check current column type
            result = conn.execute(text("""
                SELECT data_type 
                FROM information_schema.columns 
                WHERE table_name = 'audit_logs' AND column_name = 'timestamp'
            """))
            current_type = result.scalar()
            print(f"Current timestamp column type: {current_type}")
            
            if current_type == 'timestamp without time zone':
                print("\n📝 Converting TIMESTAMP to TIMESTAMPTZ...")
                
                # Step 1: Alter column to TIMESTAMPTZ (PostgreSQL will assume server timezone)
                print("  1. Altering column type to TIMESTAMPTZ...")
                conn.execute(text("""
                    ALTER TABLE audit_logs 
                    ALTER COLUMN timestamp TYPE TIMESTAMP WITH TIME ZONE 
                    USING timestamp AT TIME ZONE 'Asia/Kolkata'
                """))
                
                # Step 2: Convert all timestamps to UTC
                print("  2. Converting all timestamps to UTC...")
                conn.execute(text("""
                    UPDATE audit_logs 
                    SET timestamp = timestamp AT TIME ZONE 'UTC'
                """))
                
                print("  ✅ Column migrated to TIMESTAMPTZ with UTC values")
            elif current_type == 'timestamp with time zone':
                print("\n📝 Column is already TIMESTAMPTZ, converting values to UTC...")
                conn.execute(text("""
                    UPDATE audit_logs 
                    SET timestamp = timestamp AT TIME ZONE 'UTC'
                """))
                print("  ✅ All timestamps converted to UTC")
            else:
                print(f"  ℹ️  Column is already {current_type}")
            
            # Verify migration
            print("\n🔍 Verifying migration...")
            result = conn.execute(text("""
                SELECT id, action_type, timestamp 
                FROM audit_logs 
                ORDER BY timestamp DESC 
                LIMIT 5
            """))
            
            print("\nRecent audit logs (should now be in UTC):")
            for row in result:
                print(f"  ID {row[0]}: {row[1]} @ {row[2]}")
            
            print(f"\nCurrent UTC time: {datetime.now(timezone.utc)}")
            
            # Commit transaction
            trans.commit()
            print("\n✅ Migration completed successfully!")
            
        except Exception as e:
            trans.rollback()
            print(f"\n❌ Migration failed: {e}")
            import traceback
            traceback.print_exc()
            raise

if __name__ == "__main__":
    migrate()
