from pydantic import BaseModel, field_serializer
from datetime import datetime, timezone

class AttendanceResponse(BaseModel):
    ticket_id: int
    event_id: int
    student_prn: str
    scanned_at: datetime

    @field_serializer('scanned_at')
    def serialize_dt(self, dt: datetime, _info):
        if dt and dt.tzinfo is None:
            # If datetime is naive, assume it's UTC
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.isoformat() if dt else None

    class Config:
        from_attributes = True