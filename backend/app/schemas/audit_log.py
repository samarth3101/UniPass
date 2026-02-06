from pydantic import BaseModel, field_serializer
from datetime import datetime, timezone
from typing import Optional, Dict, Any

class AuditLogBase(BaseModel):
    action_type: str
    details: Optional[Dict[str, Any]] = None

class AuditLogCreate(AuditLogBase):
    event_id: int
    user_id: Optional[int] = None
    ip_address: Optional[str] = None

class AuditLogResponse(AuditLogBase):
    id: int
    event_id: int
    user_id: Optional[int]
    user_email: Optional[str] = None  # Include user email for display
    ip_address: Optional[str]
    timestamp: datetime

    @field_serializer('timestamp')
    def serialize_dt(self, dt: datetime, _info):
        if dt and dt.tzinfo is None:
            # If datetime is naive, assume it's UTC
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.isoformat() if dt else None

    class Config:
        from_attributes = True
