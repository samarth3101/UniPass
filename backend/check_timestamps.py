#!/usr/bin/env python3
"""
Check timestamp storage in database
"""
from datetime import datetime, timezone
from app.db.database import SessionLocal
from app.models.audit_log import AuditLog
from sqlalchemy import text

def check_timestamps():
    db = SessionLocal()
    try:
        # Get some recent audit logs
        logs = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(5).all()
        
        print("Recent Audit Logs:")
        print("=" * 80)
        for log in logs:
            print(f"\nID: {log.id}")
            print(f"Action: {log.action_type}")
            print(f"Timestamp (Python object): {log.timestamp}")
            print(f"Timestamp Type: {type(log.timestamp)}")
            print(f"Timezone Info: {log.timestamp.tzinfo}")
            print(f"ISO Format: {log.timestamp.isoformat() if log.timestamp else 'None'}")
            
            # Add UTC timezone if naive
            if log.timestamp and log.timestamp.tzinfo is None:
                utc_timestamp = log.timestamp.replace(tzinfo=timezone.utc)
                print(f"With UTC marker: {utc_timestamp.isoformat()}")
        
        print("\n" + "=" * 80)
        print("\nChecking raw database value:")
        # Query raw timestamp from database
        result = db.execute(text(
            "SELECT id, action_type, timestamp FROM audit_logs ORDER BY timestamp DESC LIMIT 5"
        )).fetchall()
        
        for row in result:
            print(f"\nID: {row[0]} | Action: {row[1]} | Raw DB timestamp: {row[2]}")
        
        print("\n" + "=" * 80)
        print(f"\nCurrent UTC time: {datetime.now(timezone.utc)}")
        print(f"Current local time: {datetime.now()}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    check_timestamps()
