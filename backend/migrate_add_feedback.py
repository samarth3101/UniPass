"""
Database Migration: Add Feedback Table

This migration adds the 'feedbacks' table to collect post-event feedback
from attended students with AI-ready fields for sentiment analysis.

Run this script from the backend directory AFTER activating your virtual environment:
    python migrate_add_feedback.py
"""

import sys
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, ForeignKey, Index, Text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.db.base import Base

# Import all models to ensure they're registered with Base
from app.models.event import Event
from app.models.ticket import Ticket
from app.models.attendance import Attendance
from app.models.student import Student
from app.models.user import User
from app.models.audit_log import AuditLog
from app.models.certificate import Certificate
from app.models.feedback import Feedback

def migrate():
    """Add feedbacks table to the database"""
    print("🔄 Starting migration: Add Feedback Table")
    print(f"📍 Database URL: {settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else settings.DATABASE_URL}")
    
    try:
        # Create engine
        engine = create_engine(settings.DATABASE_URL)
        
        # Check if feedbacks table already exists
        from sqlalchemy import inspect
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        if 'feedbacks' in existing_tables:
            print("⚠️  Feedbacks table already exists. Skipping creation.")
            
            # Verify table structure
            columns = [col['name'] for col in inspector.get_columns('feedbacks')]
            print(f"✅ Existing columns: {', '.join(columns)}")
            return True
        
        # Create only the feedbacks table
        print("📝 Creating feedbacks table...")
        Feedback.__table__.create(engine, checkfirst=True)
        
        # Verify creation
        inspector = inspect(engine)
        if 'feedbacks' in inspector.get_table_names():
            columns = [col['name'] for col in inspector.get_columns('feedbacks')]
            print(f"✅ Table 'feedbacks' created successfully!")
            print(f"✅ Columns: {', '.join(columns)}")
            
            # Verify indexes
            indexes = inspector.get_indexes('feedbacks')
            if indexes:
                print(f"✅ Indexes created: {len(indexes)}")
                for idx in indexes:
                    print(f"   - {idx['name']}: {', '.join(idx['column_names'])}")
            
            # Verify foreign keys
            fks = inspector.get_foreign_keys('feedbacks')
            if fks:
                print(f"✅ Foreign keys created: {len(fks)}")
                for fk in fks:
                    print(f"   - {fk.get('name', 'unnamed')}: {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}")
            
            print("\n🎉 Feedback table migration completed successfully!")
            return True
        else:
            print("❌ Table creation failed - table not found after creation attempt")
            return False
            
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def rollback():
    """Remove feedbacks table (use with caution!)"""
    print("⚠️  WARNING: This will DROP the feedbacks table and ALL its data!")
    confirm = input("Type 'YES' to confirm rollback: ")
    
    if confirm != "YES":
        print("❌ Rollback cancelled")
        return False
    
    try:
        engine = create_engine(settings.DATABASE_URL)
        Feedback.__table__.drop(engine, checkfirst=True)
        print("✅ Feedbacks table dropped successfully")
        return True
    except Exception as e:
        print(f"❌ Rollback failed: {str(e)}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--rollback":
        success = rollback()
    else:
        success = migrate()
    
    sys.exit(0 if success else 1)
