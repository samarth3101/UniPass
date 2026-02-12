"""
Migration Script: Add Multi-Day Event Support

This migration adds:
1. total_days column to events table (default 1 for single-day events)
2. day_number column to attendance table (tracks which day student attended)

Run this script ONCE to update your database schema.
"""

import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

def run_migration():
    """Execute the multi-day event migration"""
    
    # Create database connection
    engine = create_engine(settings.DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        print("🚀 Starting Multi-Day Event Migration...")
        print("-" * 60)
        
        # Step 1: Add total_days to events table
        print("\n📅 Step 1: Adding total_days column to events table...")
        session.execute(text("""
            ALTER TABLE events 
            ADD COLUMN IF NOT EXISTS total_days INTEGER DEFAULT 1;
        """))
        session.commit()
        print("✅ Added total_days column (default: 1)")
        
        # Step 2: Set existing events to 1 day
        print("\n🔄 Step 2: Setting existing events to single-day (total_days = 1)...")
        result = session.execute(text("""
            UPDATE events 
            SET total_days = 1 
            WHERE total_days IS NULL;
        """))
        session.commit()
        print(f"✅ Updated {result.rowcount} existing events")
        
        # Step 3: Add day_number to attendance table
        print("\n📋 Step 3: Adding day_number column to attendance table...")
        session.execute(text("""
            ALTER TABLE attendance 
            ADD COLUMN IF NOT EXISTS day_number INTEGER;
        """))
        session.commit()
        print("✅ Added day_number column")
        
        # Step 4: Set existing attendance records to day 1
        print("\n🔄 Step 4: Setting existing attendance records to day 1...")
        result = session.execute(text("""
            UPDATE attendance 
            SET day_number = 1 
            WHERE day_number IS NULL;
        """))
        session.commit()
        print(f"✅ Updated {result.rowcount} existing attendance records")
        
        # Step 5: Create index for better query performance
        print("\n⚡ Step 5: Creating indexes for performance...")
        session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_attendance_day_lookup 
            ON attendance(event_id, student_prn, day_number);
        """))
        session.commit()
        print("✅ Created composite index on (event_id, student_prn, day_number)")
        
        # Verification
        print("\n🔍 Verification:")
        print("-" * 60)
        
        # Check events table
        result = session.execute(text("""
            SELECT COUNT(*) as total, 
                   COUNT(total_days) as with_total_days
            FROM events;
        """))
        row = result.fetchone()
        print(f"Events: {row[0]} total, {row[1]} with total_days set")
        
        # Check attendance table
        result = session.execute(text("""
            SELECT COUNT(*) as total, 
                   COUNT(day_number) as with_day_number
            FROM attendance;
        """))
        row = result.fetchone()
        print(f"Attendance: {row[0]} total, {row[1]} with day_number set")
        
        print("\n" + "=" * 60)
        print("✅ MIGRATION COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("\n📊 What changed:")
        print("  • Events now support multi-day configuration (total_days)")
        print("  • Attendance tracks which day student attended (day_number)")
        print("  • All existing data preserved and set to single-day defaults")
        print("\n💡 Next steps:")
        print("  • Set total_days for multi-day events (e.g., UPDATE events SET total_days = 3 WHERE id = X)")
        print("  • Test QR scanning on different days")
        print("  • Verify certificate/feedback unlocks after all days attended")
        print("\n")
        
    except Exception as e:
        session.rollback()
        print(f"\n❌ MIGRATION FAILED: {str(e)}")
        print("\nRolling back changes...")
        sys.exit(1)
    
    finally:
        session.close()


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  UniPass Multi-Day Event Migration")
    print("=" * 60)
    
    response = input("\n⚠️  This will modify your database schema. Continue? (yes/no): ")
    
    if response.lower() == 'yes':
        run_migration()
    else:
        print("\n❌ Migration cancelled by user.")
        sys.exit(0)
