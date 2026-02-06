from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import StreamingResponse
from io import BytesIO
import qrcode
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.ticket import Ticket
from app.models.attendance import Attendance
from app.models.user import User
from app.core.permissions import require_organizer

router = APIRouter(prefix="/tickets", tags=["Tickets"])


@router.get("/qr")
def get_ticket_qr(token: str = Query(...)):
    if not token:
        raise HTTPException(status_code=400, detail="Token required")

    img = qrcode.make(token)
    buf = BytesIO()
    img.save(buf)
    buf.seek(0)

    return StreamingResponse(buf, media_type="image/png")
@router.delete("/{ticket_id}")
def delete_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_organizer)
):
    """
    Delete a ticket and its associated attendance records.
    Used by organizers/admin to remove student registration from event.
    Requires ORGANIZER or ADMIN role.
    """
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Delete associated attendance records first
    db.query(Attendance).filter(Attendance.ticket_id == ticket_id).delete()
    
    # Delete the ticket
    db.delete(ticket)
    db.commit()
    
    return {
        "status": "success",
        "message": "Ticket and attendance records deleted successfully"
    }
