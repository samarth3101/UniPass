"""
Migration: Add Lecture AI Intelligence Module
Creates lecture_reports table for storing AI-generated lecture analysis
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from app.db.database import engine

def migrate():
    """Create lecture_reports table"""
    
    migration_sql = """
    -- Create lecture_reports table
    CREATE TABLE IF NOT EXISTS lecture_reports (
        id SERIAL PRIMARY KEY,
        event_id INTEGER NOT NULL REFERENCES events(id) ON DELETE CASCADE,
        audio_filename VARCHAR NOT NULL,
        transcript TEXT,
        keywords JSONB,
        summary TEXT,
        generated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
        generated_by INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        status VARCHAR NOT NULL DEFAULT 'processing',
        error_message TEXT,
        
        CONSTRAINT fk_lecture_event FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE,
        CONSTRAINT fk_lecture_user FOREIGN KEY (generated_by) REFERENCES users(id) ON DELETE CASCADE
    );
    
    -- Create indexes for performance
    CREATE INDEX IF NOT EXISTS idx_lecture_reports_event_id ON lecture_reports(event_id);
    CREATE INDEX IF NOT EXISTS idx_lecture_reports_generated_by ON lecture_reports(generated_by);
    CREATE INDEX IF NOT EXISTS idx_lecture_reports_status ON lecture_reports(status);
    CREATE INDEX IF NOT EXISTS idx_lecture_reports_generated_at ON lecture_reports(generated_at);
    """
    
    with engine.connect() as conn:
        print("🔄 Creating lecture_reports table...")
        conn.execute(text(migration_sql))
        conn.commit()
        print("✅ lecture_reports table created successfully!")
        
        # Verify table creation
        result = conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_name = 'lecture_reports'
        """))
        
        if result.fetchone():
            print("✅ Migration verified: lecture_reports table exists")
        else:
            print("❌ Migration verification failed")
            return False
    
    return True


if __name__ == "__main__":
    print("\n" + "="*60)
    print("CORTEX LECTURE INTELLIGENCE ENGINE - DATABASE MIGRATION")
    print("="*60 + "\n")
    
    try:
        success = migrate()
        if success:
            print("\n✅ Migration completed successfully!")
            print("\nNext steps:")
            print("1. Upload audio files via POST /ai/lecture/upload/{event_id}")
            print("2. View reports via GET /ai/lecture/report/{event_id}")
        else:
            print("\n❌ Migration failed!")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Migration error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
