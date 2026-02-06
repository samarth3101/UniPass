from pydantic import BaseModel, EmailStr
from typing import Optional
from app.models.user import UserRole

class UserCreate(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    password: str
    role: Optional[UserRole] = UserRole.SCANNER  # Default to scanner for new users


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: Optional[str] = None
    role: UserRole

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Response model for login/signup with token and user info"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse