#!/usr/bin/env python3
"""Create a fresh admin user for testing"""
import sys
sys.path.append('/Users/samarthpatil/Desktop/UniPass/backend')

from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.user import User, UserRole
from passlib.context import CryptContext

# Use same password context as auth.py
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

db = SessionLocal()

# Delete existing admin@test.com if it exists
existing = db.query(User).filter(User.email == "admin@test.com").first()
if existing:
    db.delete(existing)
    db.commit()
    print("🗑️  Deleted old admin@test.com")

# Create fresh admin
admin = User(
    email="admin@test.com",
    full_name="Admin User",
    password_hash=pwd_context.hash("admin123"),
    role=UserRole.ADMIN
)
db.add(admin)
db.commit()
print("✅ Created fresh admin@test.com")
print(f"   Email: admin@test.com")
print(f"   Password: admin123")
print(f"   Role: {admin.role.value}")

# Verify the password works
from app.routes.auth import verify_password
if verify_password("admin123", admin.password_hash):
    print("✅ Password verification successful!")
else:
    print("❌ Password verification failed!")

db.close()
