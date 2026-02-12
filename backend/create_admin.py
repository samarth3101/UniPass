#!/usr/bin/env python3
"""Create admin user for testing"""
import sys
sys.path.append('/Users/samarthpatil/Desktop/UniPass/backend')

from sqlalchemy.orm import Session
from app.db.database import engine, SessionLocal
from app.models.user import User, UserRole
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

db = SessionLocal()

# Check if admin exists
admin = db.query(User).filter(User.email == "admin@test.com").first()

if admin:
    # Update password
    admin.hashed_password = pwd_context.hash("admin123")
    db.commit()
    print("✅ Updated admin@test.com password to: admin123")
else:
    # Create admin
    admin = User(
        email="admin@test.com",
        hashed_password=pwd_context.hash("admin123"),
        role=UserRole.ADMIN
    )
    db.add(admin)
    db.commit()
    print("✅ Created admin@test.com with password: admin123")

db.close()
