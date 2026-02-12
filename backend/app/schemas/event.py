from datetime import datetime, timezone
from pydantic import BaseModel, field_serializer, field_validator
from typing import Optional, List


class EventCreate(BaseModel):
    title: str
    description: Optional[str] = None
    location: Optional[str] = None
    start_time: datetime
    end_time: datetime
    total_days: Optional[int] = 1  # Number of days event spans (default: 1)

    @field_validator('start_time', 'end_time', mode='before')
    @classmethod
    def parse_datetime(cls, v):
        if isinstance(v, str):
            # Parse ISO string and ensure it has timezone info
            dt = datetime.fromisoformat(v.replace('Z', '+00:00'))
            # If no timezone, assume UTC
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        return v


class EventResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    location: Optional[str] = None
    start_time: datetime
    end_time: datetime
    created_at: datetime
    share_slug: str
    total_days: Optional[int] = 1  # Number of days event spans

    @field_serializer('created_at', 'start_time', 'end_time')
    def serialize_dt(self, dt: datetime, _info):
        if dt:
            # Database stores naive UTC times, add UTC timezone for serialization
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            # Always return ISO format with timezone
            return dt.isoformat()
        return None

    class Config:
        from_attributes = True


class EventsPaginatedResponse(BaseModel):
    """Paginated response for events list"""
    total: int
    skip: int
    limit: int
    events: List[EventResponse]