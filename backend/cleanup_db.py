"""
Database Cleanup Script
Deletes all data for fresh RBAC testing
"""

from sqlalchemy import create_engine, text
from app.core.config import settings

def cleanup_database():
    engine = create_engine(settings.DATABASE_URL)
    
    print('🗑️  Cleaning database for fresh testing...\n')
    
    with engine.connect() as conn:
        # Delete in correct order (respecting foreign keys)
        
        # 1. Delete attendance records
        result = conn.execute(text('DELETE FROM attendance'))
        print(f'✅ Deleted {result.rowcount} attendance records')
        
        # 2. Delete tickets
        result = conn.execute(text('DELETE FROM tickets'))
        print(f'✅ Deleted {result.rowcount} tickets')
        
        # 3. Delete events
        result = conn.execute(text('DELETE FROM events'))
        print(f'✅ Deleted {result.rowcount} events')
        
        # 4. Delete students  
        result = conn.execute(text('DELETE FROM students'))
        print(f'✅ Deleted {result.rowcount} students')
        
        # 5. Finally delete users
        result = conn.execute(text('DELETE FROM users'))
        print(f'✅ Deleted {result.rowcount} users')
        
        conn.commit()
        
        print('\n✅ Database cleaned successfully!')
        print('🎯 Ready for fresh RBAC testing')
        print('\nNext steps:')
        print('1. Go to http://localhost:3000/signup')
        print('2. Create test accounts:')
        print('   - admin@test.com (ADMIN role)')
        print('   - organizer@test.com (ORGANIZER role)')
        print('   - scanner@test.com (SCANNER role)')
        print('3. Test each role\'s access permissions')

if __name__ == "__main__":
    cleanup_database()
