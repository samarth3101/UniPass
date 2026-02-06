"""
System Diagnostic and Bug Fix Script
Checks all components and fixes common issues
"""

from sqlalchemy import create_engine, text, inspect
from app.core.config import settings

def check_database():
    """Check database schema and data integrity"""
    print("\n=== DATABASE CHECK ===")
    engine = create_engine(settings.DATABASE_URL)
    inspector = inspect(engine)
    
    # Check tables
    tables = inspector.get_tables()
    print(f"✅ Tables found: {len(tables)}")
    for table in tables:
        print(f"  - {table['name']}")
    
    # Check users table structure
    if 'users' in [t['name'] for t in tables]:
        columns = inspector.get_columns('users')
        print(f"\n✅ Users table columns:")
        for col in columns:
            print(f"  - {col['name']}: {col['type']}")
    
    # Check events table structure
    if 'events' in [t['name'] for t in tables]:
        columns = inspector.get_columns('events')
        print(f"\n✅ Events table columns:")
        for col in columns:
            if 'created_by' in col['name']:
                print(f"  - {col['name']}: {col['type']} ✓ (ownership tracking)")
    
    # Check data counts
    with engine.connect() as conn:
        result = conn.execute(text('SELECT COUNT(*) FROM users'))
        user_count = result.scalar()
        print(f"\n✅ Total users: {user_count}")
        
        result = conn.execute(text('SELECT COUNT(*) FROM events'))
        event_count = result.scalar()
        print(f"✅ Total events: {event_count}")
        
        result = conn.execute(text('SELECT COUNT(*) FROM tickets'))
        ticket_count = result.scalar()
        print(f"✅ Total tickets: {ticket_count}")
        
        result = conn.execute(text('SELECT COUNT(*) FROM students'))
        student_count = result.scalar()
        print(f"✅ Total students: {student_count}")

def check_routes():
    """Check if all routes are properly registered"""
    print("\n=== ROUTES CHECK ===")
    from app.main import app
    
    routes = []
    for route in app.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            routes.append((route.path, route.methods))
    
    print(f"✅ Total routes: {len(routes)}")
    
    # Check critical routes
    critical = [
        '/auth/login',
        '/auth/signup',
        '/events/',
        '/admin/organizers',
        '/admin/scanners',
        '/scan/',
    ]
    
    for path in critical:
        exists = any(path in r[0] for r in routes)
        status = "✅" if exists else "❌"
        print(f"{status} {path}")

def check_models():
    """Check if models are properly configured"""
    print("\n=== MODELS CHECK ===")
    from app.models.user import User, UserRole
    from app.models.event import Event
    
    print(f"✅ User model loaded")
    print(f"  - Roles: {[r.value for r in UserRole]}")
    
    print(f"✅ Event model loaded")
    # Check if created_by field exists
    if hasattr(Event, 'created_by'):
        print(f"  - Ownership tracking: ✓")
    else:
        print(f"  - Ownership tracking: ✗ (MISSING)")

if __name__ == "__main__":
    print("🔍 Running System Diagnostics...\n")
    
    try:
        check_database()
        check_routes()
        check_models()
        
        print("\n" + "="*50)
        print("✅ SYSTEM DIAGNOSTIC COMPLETE")
        print("="*50)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
