import sys
sys.path.insert(0, '/Users/samarthpatil/Desktop/UNIPASS/UniPass/backend')

from app.db.database import SessionLocal
from app.models.ticket import Ticket
from app.models.attendance import Attendance
from app.models.event import Event

db = SessionLocal()

try:
    # Test with PRN 12345
    prn = "12345"
    print(f"Testing PRN: {prn}")
    
    tickets = db.query(Ticket).filter(Ticket.student_prn == prn).all()
    print(f"Found {len(tickets)} tickets")
    
    attendance_records = (
        db.query(Attendance, Event, Ticket)
        .join(Ticket, Attendance.ticket_id == Ticket.id)
        .join(Event, Ticket.event_id == Event.id)
        .filter(Ticket.student_prn == prn)
        .order_by(Attendance.scanned_at.desc())
        .all()
    )
    print(f"Found {len(attendance_records)} attendance records")
    
    for ticket in tickets[:2]:  # Test first 2
        print(f"\nTicket ID: {ticket.id}, Event ID: {ticket.event_id}")
        
        # Check if attendance exists for this ticket
        attendance = next((att for att, _, t in attendance_records if t.id == ticket.id), None)
        has_attendance = attendance is not None
        
        print(f"  Has attendance: {has_attendance}")
        if has_attendance:
            print(f"  Attendance type: {type(attendance)}")
            print(f"  Attendance scanned_at: {attendance.scanned_at}")
            try:
                iso_date = attendance.scanned_at.isoformat() if attendance.scanned_at else None
                print(f"  ISO format: {iso_date}")
            except Exception as e:
                print(f"  ERROR converting to ISO: {e}")
        
except Exception as e:
    import traceback
    print(f"\nERROR: {e}")
    traceback.print_exc()
finally:
    db.close()
