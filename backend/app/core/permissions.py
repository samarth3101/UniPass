"""
Role-Based Access Control (RBAC) Dependencies
Provides FastAPI dependencies for checking user roles
"""

from fastapi import Depends, HTTPException, status, Request
from typing import Optional
from app.models.user import User, UserRole
from app.security.jwt import get_current_user, decode_access_token
from app.db.database import get_db
from sqlalchemy.orm import Session


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency to ensure current user has ADMIN role
    Usage: @router.get("/admin-only", dependencies=[Depends(require_admin)])
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


def require_organizer(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency to ensure current user has ORGANIZER or ADMIN role
    Organizers can manage events and view analytics
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.ORGANIZER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Event organizer access required"
        )
    return current_user


def require_scanner(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency to ensure current user is authenticated
    Any authenticated user can scan (SCANNER, ORGANIZER, ADMIN)
    """
    # All authenticated users can scan
    return current_user


def get_user_role(current_user: User = Depends(get_current_user)) -> UserRole:
    """
    Dependency to get current user's role
    Useful for conditional logic in routes
    """
    return current_user.role


def get_current_user_optional(
    request: Request,
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Dependency to optionally get current user (for unauthenticated scanning)
    Returns None if not authenticated, does not raise HTTPException
    """
    auth_header = request.headers.get("Authorization")
    
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    
    token = auth_header.replace("Bearer ", "")
    
    try:
        payload = decode_access_token(token)
        user_id = payload.get("user_id")
        
        if not user_id:
            return None
        
        user = db.query(User).filter(User.id == user_id).first()
        return user
    except:
        return None
