"""
Student Schemas
Pydantic models for student data validation
"""

from pydantic import BaseModel, EmailStr
from typing import Optional


class StudentBase(BaseModel):
    prn: str
    name: str
    email: Optional[EmailStr] = None
    department: Optional[str] = None
    year: Optional[int] = None


class StudentCreate(StudentBase):
    """Schema for creating a new student"""
    pass


class StudentResponse(StudentBase):
    """Schema for student response"""
    id: int

    class Config:
        from_attributes = True
