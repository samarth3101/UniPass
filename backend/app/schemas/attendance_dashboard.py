from pydantic import BaseModel
from datetime import datetime
from typing import List

class AttendanceItem(BaseModel):
    student_prn: str
    scanned_at: datetime

    class Config:
        from_attributes = True


class AttendanceSummary(BaseModel):
    event_id: int
    total_present: int
    total_registered: int = 0
    total_attended: int = 0