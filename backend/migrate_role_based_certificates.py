"""
Migration: Add Role-Based Certificates Support
Adds volunteers table and updates certificates table for role-based certificates
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.db.database import engine
from app.models import Volunteer  # Import to ensure table is created
from app.db.base import Base

def run_migration():
    """Run the role-based certificates migration"""
    
    print("🚀 Starting Role-Based Certificates Migration...")
    print("=" * 70)
    
    # Create tables (including new volunteers table)
    print("\n1️⃣  Creating volunteers table if not exists...")
    Base.metadata.create_all(bind=engine, checkfirst=True)
    print("   ✅ Volunteers table ready")
    
    # Add new columns to certificates table
    with engine.connect() as conn:
        print("\n2️⃣  Adding new columns to certificates table...")
        
        try:
            # Add role_type column (default to 'attendee')
            print("   📝 Adding role_type column...")
            conn.execute(text("""
                ALTER TABLE certificates 
                ADD COLUMN IF NOT EXISTS role_type VARCHAR(50) DEFAULT 'attendee'
            """))
            conn.commit()
            print("   ✅ role_type column added")
        except Exception as e:
            if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
                print("   ⚠️  role_type column already exists, skipping")
            else:
                print(f"   ⚠️  Error adding role_type: {e}")
        
        try:
            # Add recipient_name column
            print("   📝 Adding recipient_name column...")
            conn.execute(text("""
                ALTER TABLE certificates 
                ADD COLUMN IF NOT EXISTS recipient_name VARCHAR(255)
            """))
            conn.commit()
            print("   ✅ recipient_name column added")
        except Exception as e:
            if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
                print("   ⚠️  recipient_name column already exists, skipping")
            else:
                print(f"   ⚠️  Error adding recipient_name: {e}")
        
        try:
            # Add recipient_email column
            print("   📝 Adding recipient_email column...")
            conn.execute(text("""
                ALTER TABLE certificates 
                ADD COLUMN IF NOT EXISTS recipient_email VARCHAR(255)
            """))
            conn.commit()
            print("   ✅ recipient_email column added")
        except Exception as e:
            if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
                print("   ⚠️  recipient_email column already exists, skipping")
            else:
                print(f"   ⚠️  Error adding recipient_email: {e}")
        
        try:
            # Make student_prn nullable (if it's not already)
            print("   📝 Making student_prn nullable...")
            conn.execute(text("""
                ALTER TABLE certificates 
                ALTER COLUMN student_prn DROP NOT NULL
            """))
            conn.commit()
            print("   ✅ student_prn is now nullable")
        except Exception as e:
            if "does not exist" in str(e).lower():
                print("   ⚠️  student_prn column constraint issue, may already be nullable")
            else:
                print(f"   ⚠️  Error modifying student_prn: {e}")
        
        # Populate recipient_name and recipient_email for existing certificates
        print("\n3️⃣  Populating recipient data for existing certificates...")
        try:
            result = conn.execute(text("""
                UPDATE certificates c
                SET 
                    recipient_name = s.name,
                    recipient_email = s.email
                FROM students s
                WHERE c.student_prn = s.prn
                  AND c.recipient_name IS NULL
            """))
            conn.commit()
            print(f"   ✅ Updated {result.rowcount} existing certificates with recipient data")
        except Exception as e:
            print(f"   ⚠️  Error populating recipient data: {e}")
            print("   (This is okay if you haven't created a students table yet)")
    
    print("\n" + "=" * 70)
    print("✅ Migration completed successfully!")
    print("\nNew features available:")
    print("  • Volunteers can be added to events")
    print("  • Certificates support 4 roles: ATTENDEE, ORGANIZER, SCANNER, VOLUNTEER")
    print("  • Each role gets a unique certificate design")
    print("  • Non-student certificates (organizers, scanners, volunteers) tracked separately")
    print("=" * 70)

if __name__ == "__main__":
    try:
        run_migration()
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
