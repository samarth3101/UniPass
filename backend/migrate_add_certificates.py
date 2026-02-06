"""
Database Migration: Add Certificates Table

This migration adds the 'certificates' table to track certificate issuance
for event attendees.

Run this script from the backend directory AFTER activating your virtual environment:
    python migrate_add_certificates.py
"""

import sys
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, ForeignKey, Index
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

def migrate():
    """Add certificates table to the database"""
    print("🔄 Starting migration: Add Certificates Table")
    print(f"📍 Database URL: {settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else settings.DATABASE_URL}")
    
    try:
        # Create engine
        engine = create_engine(settings.DATABASE_URL)
        
        # Check if certificates table already exists
        from sqlalchemy import inspect
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        if 'certificates' in existing_tables:
            print("⚠️  Certificates table already exists. Skipping creation.")
            
            # Verify table structure
            columns = [col['name'] for col in inspector.get_columns('certificates')]
            print(f"✅ Existing columns: {', '.join(columns)}")
            return True
        
        # Create only the certificates table
        print("📝 Creating certificates table...")
        Certificate.__table__.create(engine, checkfirst=True)
        
        # Verify creation
        inspector = inspect(engine)
        columns = [col['name'] for col in inspector.get_columns('certificates')]
        
        print("✅ Migration completed successfully!")
        print(f"✅ Certificates table created with columns: {', '.join(columns)}")
        print()
        print("📋 Certificate tracking features added:")
        print("   • Tracks which students received certificates")
        print("   • Prevents duplicate certificate issuance")
        print("   • Records email delivery status")
        print("   • Links certificates to events and students")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def verify_migration():
    """Verify the migration was successful"""
    print("\n🔍 Verifying migration...")
    try:
        engine = create_engine(settings.DATABASE_URL)
        from sqlalchemy import inspect
        inspector = inspect(engine)
        
        if 'certificates' not in inspector.get_table_names():
            print("❌ Verification failed: certificates table not found")
            return False
        
        columns = [col['name'] for col in inspector.get_columns('certificates')]
        required_columns = ['id', 'event_id', 'student_prn', 'certificate_id', 'issued_at', 'email_sent', 'email_sent_at']
        
        missing_columns = [col for col in required_columns if col not in columns]
        if missing_columns:
            print(f"❌ Verification failed: Missing columns: {', '.join(missing_columns)}")
            return False
        
        print("✅ Verification passed: All required columns present")
        return True
        
    except Exception as e:
        print(f"❌ Verification failed: {str(e)}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("Certificate Generation System - Database Migration")
    print("=" * 60)
    print()
    
    # Run migration
    success = migrate()
    
    if success:
        # Verify migration
        verify_migration()
        print()
        print("🎉 Migration complete! You can now use the certificate features.")
        print()
        print("📌 Next steps:")
        print("   1. Restart your backend server")
        print("   2. Navigate to an event in the Event Control Center")
        print("   3. Click 'Push Certificates' to send certificates to attendees")
        sys.exit(0)
    else:
        print()
        print("❌ Migration failed. Please check the errors above.")
        sys.exit(1)
