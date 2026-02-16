"""
Migration: Add guest_speaker column to events table
Run this script once to add the new column to existing database
"""

from sqlalchemy import text
from app.db.database import engine

def migrate():
    print("=" * 70)
    print("MIGRATION: Add guest_speaker column to events table")
    print("=" * 70)
    
    with engine.connect() as conn:
        # Check if column already exists (PostgreSQL syntax)
        result = conn.execute(text("""
            SELECT COUNT(*) 
            FROM information_schema.columns 
            WHERE table_name='events' AND column_name='guest_speaker'
        """))
        
        exists = result.scalar()
        
        if exists:
            print("\n✓ Column 'guest_speaker' already exists in events table")
            print("  No migration needed.\n")
            return
        
        print("\n→ Adding 'guest_speaker' column to events table...")
        
        # Add the column
        conn.execute(text("""
            ALTER TABLE events 
            ADD COLUMN guest_speaker VARCHAR NULL
        """))
        
        conn.commit()
        
        print("✓ Column added successfully!")
        
        # Verify the column was added
        result = conn.execute(text("""
            SELECT COUNT(*) 
            FROM information_schema.columns 
            WHERE table_name='events' AND column_name='guest_speaker'
        """))
        
        if result.scalar():
            print("✓ Migration verified - column exists in database")
        else:
            print("✗ Warning: Column may not have been added correctly")
        
        print("\n" + "=" * 70)
        print("MIGRATION COMPLETED SUCCESSFULLY")
        print("=" * 70 + "\n")

if __name__ == "__main__":
    try:
        migrate()
    except Exception as e:
        print(f"\n✗ Migration failed: {e}\n")
        raise
