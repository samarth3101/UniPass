#!/usr/bin/env python3
"""Restore original user setup with admin2315 password"""
import sys
sys.path.append('/Users/samarthpatil/Desktop/UniPass/backend')

from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.user import User, UserRole
from passlib.context import CryptContext

# Use same password context as auth.py
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

db = SessionLocal()

# Define original users with admin2315 password
users_to_create = [
    {
        "email": "admin@test.com",
        "password": "admin2315",
        "role": UserRole.ADMIN,
        "full_name": "Admin User"
    },
    {
        "email": "organizer@test.com",
        "password": "admin2315",
        "role": UserRole.ORGANIZER,
        "full_name": "Organizer User"
    },
    {
        "email": "scanner@test.com",
        "password": "admin2315",
        "role": UserRole.SCANNER,
        "full_name": "Scanner User"
    }
]

print("Setting up original users with password: admin2315\n")

for user_data in users_to_create:
    existing = db.query(User).filter(User.email == user_data["email"]).first()
    
    if existing:
        # Update existing user
        existing.password_hash = pwd_context.hash(user_data["password"])
        existing.role = user_data["role"]
        if user_data.get("full_name"):
            existing.full_name = user_data["full_name"]
        db.commit()
        print(f"✅ Updated {user_data['email']}")
    else:
        # Create new user
        new_user = User(
            email=user_data["email"],
            full_name=user_data["full_name"],
            password_hash=pwd_context.hash(user_data["password"]),
            role=user_data["role"]
        )
        db.add(new_user)
        db.commit()
        print(f"✅ Created {user_data['email']}")
    
    print(f"   Email: {user_data['email']}")
    print(f"   Password: {user_data['password']}")
    print(f"   Role: {user_data['role'].value}\n")

# Verify passwords work
print("\n🔍 Verifying passwords...")
from app.routes.auth import verify_password
for user_data in users_to_create:
    user = db.query(User).filter(User.email == user_data["email"]).first()
    if user and verify_password(user_data["password"], user.password_hash):
        print(f"✅ {user_data['email']} password verified")
    else:
        print(f"❌ {user_data['email']} password verification FAILED!")

db.close()

print("\n" + "="*50)
print("All users ready with password: admin2315")
print("="*50)
