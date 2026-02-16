#!/usr/bin/env python3
"""Create test admin user"""
import sys
sys.path.append('/Users/samarthpatil/Desktop/UniPass/backend')

from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.user import User, UserRole
from passlib.context import CryptContext

# Use same password context as auth.py
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

db = SessionLocal()

# Check if admin exists
admin = db.query(User).filter(User.email == "testadmin@unipass.com").first()

if admin:
    # Update password
    admin.password_hash = pwd_context.hash("test123456")
    db.commit()
    print("✅ Updated testadmin@unipass.com password to: test123456")
else:
    # Create admin
    admin = User(
        email="testadmin@unipass.com",
        full_name="Test Admin",
        password_hash=pwd_context.hash("test123456"),
        role=UserRole.ADMIN
    )
    db.add(admin)
    db.commit()
    print("✅ Created testadmin@unipass.com with password: test123456")

print(f"   Email: testadmin@unipass.com")
print(f"   Password: test123456")
print(f"   Role: {admin.role.value}")

db.close()
