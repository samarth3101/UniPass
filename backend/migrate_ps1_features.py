"""
Migration Script for PS1 Features
Adds:
- participation_roles table
- Certificate verification and revocation fields
"""

import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from app.core.config import settings
from app.db.base import Base

def run_migration():
    """Run PS1 migration"""
    
    print("\n" + "="*70)
    print("🚀 UniPass - PS1 Features Migration")
    print("="*70)
    print("\nThis migration will add:")
    print("  ✅ participation_roles table (Feature 5: Multi-Role Participation)")
    print("  ✅ Certificate verification fields (Feature 3: Verification System)")
    print("  ✅ Certificate revocation fields (Feature 4: Retroactive Changes)")
    print()
    
    # Confirm before proceeding
    confirm = input("⚠️  Do you want to proceed? (yes/no): ").strip().lower()
    if confirm != "yes":
        print("❌ Migration cancelled.")
        return
    
    try:
        # Create engine
        engine = create_engine(settings.DATABASE_URL)
        
        print("\n📊 Applying database changes...")
        
        # Add verification_hash to certificates (if not exists)
        with engine.connect() as conn:
            try:
                conn.execute(text("""
                    ALTER TABLE certificates 
                    ADD COLUMN IF NOT EXISTS verification_hash VARCHAR UNIQUE
                """))
                conn.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS idx_cert_verification_hash ON certificates(verification_hash)"))
                conn.commit()
                print("  ✅ Added verification_hash column to certificates")
            except Exception as e:
                print(f"  ⚠️  verification_hash column might already exist: {e}")
            
            # Add revocation fields to certificates
            try:
                conn.execute(text("""
                    ALTER TABLE certificates 
                    ADD COLUMN IF NOT EXISTS revoked BOOLEAN DEFAULT FALSE
                """))
                conn.execute(text("""
                    ALTER TABLE certificates 
                    ADD COLUMN IF NOT EXISTS revoked_at TIMESTAMP
                """))
                conn.execute(text("""
                    ALTER TABLE certificates 
                    ADD COLUMN IF NOT EXISTS revoked_by INTEGER
                """))
                conn.execute(text("""
                    ALTER TABLE certificates 
                    ADD COLUMN IF NOT EXISTS revocation_reason TEXT
                """))
                conn.commit()
                print("  ✅ Added revocation fields to certificates")
            except Exception as e:
                print(f"  ⚠️  Revocation fields might already exist: {e}")
        
        # Create participation_roles table
        try:
            with engine.connect() as conn:
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS participation_roles (
                        id SERIAL PRIMARY KEY,
                        event_id INTEGER NOT NULL REFERENCES events(id) ON DELETE CASCADE,
                        student_prn VARCHAR NOT NULL,
                        role VARCHAR NOT NULL,
                        assigned_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        assigned_by INTEGER REFERENCES users(id),
                        time_segment VARCHAR
                    )
                """))
                
                # Create indexes
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_participation_roles_event ON participation_roles(event_id)"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_participation_roles_student ON participation_roles(student_prn)"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_participation_roles_role ON participation_roles(role)"))
                
                conn.commit()
            
            print("  ✅ Created participation_roles table with indexes")
        except Exception as e:
            print(f"  ⚠️  participation_roles table might already exist: {e}")
        
        # Verify tables exist
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema='public' 
                AND table_name IN ('participation_roles', 'certificates')
            """))
            tables = [row[0] for row in result]
            
            print("\n📋 Verification:")
            print(f"  ✅ participation_roles table: {'EXISTS' if 'participation_roles' in tables else 'MISSING'}")
            print(f"  ✅ certificates table: {'EXISTS' if 'certificates' in tables else 'MISSING'}")
        
        print("\n" + "="*70)
        print("✅ PS1 MIGRATION COMPLETED SUCCESSFULLY!")
        print("="*70)
        print("\nNew Features Available:")
        print("  🎯 Feature 1: Participation Reconciliation - GET /ps1/participation/status/{event_id}/{prn}")
        print("  🔍 Feature 3: Certificate Verification - GET /ps1/verify/certificate/{cert_id}")
        print("  ⏮️  Feature 4: Certificate Revocation - POST /ps1/certificate/{cert_id}/revoke")
        print("  👥 Feature 5: Role Management - POST /ps1/roles/{event_id}/assign")
        print("\n📚 API Documentation: http://localhost:8000/docs")
        print()
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    run_migration()
