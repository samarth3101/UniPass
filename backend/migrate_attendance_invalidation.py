"""
Database Migration: Add Attendance Invalidation Fields

This migration adds invalidation tracking fields to the 'attendance' table
to support PS1 Feature 4 (Retroactive Change & Audit Trail Engine).

Run this script from the backend directory AFTER activating your virtual environment:
    python migrate_attendance_invalidation.py
"""

import sys
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, ForeignKey, Text, text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.db.base import Base

def migrate():
    """Add invalidation columns to attendance table"""
    print("🔄 Starting migration: Add Attendance Invalidation Fields")
    print(f"📍 Database URL: {settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else settings.DATABASE_URL}")
    
    try:
        engine = create_engine(settings.DATABASE_URL)
        
        # Check if columns already exist
        from sqlalchemy import inspect
        inspector = inspect(engine)
        
        if 'attendance' not in inspector.get_table_names():
            print("❌ Attendance table does not exist. Run base migrations first.")
            return False
        
        existing_columns = [col['name'] for col in inspector.get_columns('attendance')]
        print(f"📋 Existing columns: {', '.join(existing_columns)}")
        
        # Columns to add
        columns_to_add = [
            ('invalidated', 'BOOLEAN DEFAULT FALSE'),
            ('invalidated_at', 'TIMESTAMP'),
            ('invalidated_by', 'INTEGER'),
            ('invalidation_reason', 'TEXT')
        ]
        
        columns_added = []
        columns_skipped = []
        
        with engine.connect() as conn:
            for col_name, col_type in columns_to_add:
                if col_name in existing_columns:
                    columns_skipped.append(col_name)
                    continue
                
                print(f"➕ Adding column: {col_name} ({col_type})")
                
                # Add column (works for both SQLite and PostgreSQL)
                try:
                    conn.execute(text(f"ALTER TABLE attendance ADD COLUMN {col_name} {col_type}"))
                    conn.commit()
                    columns_added.append(col_name)
                    print(f"   ✅ Added {col_name}")
                except Exception as e:
                    print(f"   ⚠️  Warning for {col_name}: {e}")
            
            # Add foreign key constraint for invalidated_by (if PostgreSQL)
            if 'invalidated_by' in columns_added:
                try:
                    conn.execute(text(
                        "ALTER TABLE attendance ADD CONSTRAINT fk_attendance_invalidated_by "
                        "FOREIGN KEY (invalidated_by) REFERENCES users(id)"
                    ))
                    conn.commit()
                    print("   ✅ Added foreign key constraint for invalidated_by")
                except Exception as e:
                    # SQLite doesn't support adding foreign keys to existing tables
                    print(f"   ℹ️  Note: {e}")
        
        # Summary
        print("\n" + "="*60)
        if columns_added:
            print(f"✅ Successfully added {len(columns_added)} columns:")
            for col in columns_added:
                print(f"   - {col}")
        
        if columns_skipped:
            print(f"⏭️  Skipped {len(columns_skipped)} existing columns:")
            for col in columns_skipped:
                print(f"   - {col}")
        
        print("="*60)
        print("✅ Migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = migrate()
    sys.exit(0 if success else 1)
