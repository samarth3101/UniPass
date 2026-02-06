from pydantic import BaseModel
from datetime import datetime

class TicketResponse(BaseModel):
    id: int
    event_id: int
    student_prn: str
    issued_at: datetime
    token: str

    class Config:
        from_attributes = True