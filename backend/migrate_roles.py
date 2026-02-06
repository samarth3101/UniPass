"""
Database migration script to update user roles
Run this to update the existing users table with the new role enum
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.database import engine
from sqlalchemy import text

def migrate_roles():
    """Update user table to use new role enum"""
    
    print("🔄 Starting role migration...")
    
    with engine.connect() as conn:
        try:
            # Check if role column exists and what type it is
            result = conn.execute(text("""
                SELECT data_type 
                FROM information_schema.columns 
                WHERE table_name = 'users' AND column_name = 'role'
            """))
            
            current_type = result.scalar()
            print(f"Current role column type: {current_type}")
            
            if current_type == 'character varying':
                print("✅ Role column already exists as VARCHAR")
                print("Updating existing roles to match new enum values...")
                
                # Update any 'admin' roles (keep as is)
                conn.execute(text("""
                    UPDATE users 
                    SET role = 'admin' 
                    WHERE role = 'admin' OR role = 'teacher'
                """))
                
                # Set default role for any NULL or unknown roles
                conn.execute(text("""
                    UPDATE users 
                    SET role = 'scanner' 
                    WHERE role IS NULL OR role NOT IN ('admin', 'organizer', 'scanner')
                """))
                
                conn.commit()
                print("✅ User roles updated successfully!")
                
            else:
                print(f"⚠️  Unexpected column type: {current_type}")
                print("The database schema may need manual adjustment")
                
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            conn.rollback()
            raise

    print("\n✅ Migration completed!")
    print("\nRole values:")
    print("  - admin: Full system access")
    print("  - organizer: Manage events, view analytics")
    print("  - scanner: Scan QR codes only")

if __name__ == "__main__":
    migrate_roles()
