"""
Migration script to add full_name column to users table
Run this before using the new signup with name field
"""

from sqlalchemy import create_engine, Column, String, text
from app.core.config import settings

def migrate():
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        # Add full_name column if it doesn't exist
        try:
            conn.execute(text("""
                ALTER TABLE users 
                ADD COLUMN IF NOT EXISTS full_name VARCHAR;
            """))
            conn.commit()
            print("✅ Successfully added full_name column to users table")
        except Exception as e:
            print(f"❌ Error during migration: {e}")
            conn.rollback()

if __name__ == "__main__":
    migrate()
