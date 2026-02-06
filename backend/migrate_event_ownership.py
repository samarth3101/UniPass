"""
Migration: Add created_by column to events table
This tracks which user created each event for ownership filtering
"""

from app.db.database import engine
from sqlalchemy import text

def run_migration():
    with engine.connect() as conn:
        print('🔄 Adding created_by column to events table...')
        try:
            conn.execute(text('ALTER TABLE events ADD COLUMN created_by INTEGER'))
            conn.execute(text('ALTER TABLE events ADD FOREIGN KEY (created_by) REFERENCES users(id)'))
            conn.commit()
            print('✅ Column added successfully')
        except Exception as e:
            conn.rollback()  # Rollback failed transaction
            if 'already exists' in str(e).lower() or 'duplicate' in str(e).lower():
                print('✅ Column already exists')
            else:
                print(f'❌ Error: {e}')
                return
        
        print('\n🔄 Assigning existing events to first admin user...')
        result = conn.execute(text("SELECT id FROM users WHERE role = 'ADMIN' ORDER BY id LIMIT 1"))
        admin_id = result.scalar()
        
        if admin_id:
            result = conn.execute(text(f'UPDATE events SET created_by = {admin_id} WHERE created_by IS NULL'))
            conn.commit()
            print(f'✅ Assigned {result.rowcount} events to admin (ID: {admin_id})')
        else:
            print('⚠️  No admin user found - existing events will have NULL creator')
        
        print('\n✅ Migration complete!')
        print('\n📋 Summary:')
        print('  - created_by column added to events table')
        print('  - Existing events assigned to admin user')
        print('  - New events will automatically track creator')

if __name__ == '__main__':
    run_migration()
