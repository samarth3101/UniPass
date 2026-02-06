from sqlalchemy import Column, Integer, String, Enum as SQLEnum
from app.db.base import Base
import enum

class UserRole(str, enum.Enum):
    """User roles for Role-Based Access Control"""
    ADMIN = "ADMIN"  # Full system access
    ORGANIZER = "ORGANIZER"  # Can manage events and view analytics
    SCANNER = "SCANNER"  # Can only scan QR codes

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=True)
    password_hash = Column(String, nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.SCANNER, nullable=False)