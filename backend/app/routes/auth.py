from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.db.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, TokenResponse, UserResponse
from app.security.jwt import create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])
limiter = Limiter(key_func=get_remote_address)

pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    deprecated="auto"
)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


@router.post("/signup", response_model=TokenResponse)
@limiter.limit("10/hour")  # Limit signup attempts
def signup(request: Request, user: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user with specified role
    Default role is SCANNER if not provided
    """
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(
        email=user.email,
        full_name=user.full_name,
        password_hash=hash_password(user.password),
        role=user.role
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Create access token with role
    token = create_access_token({
        "user_id": new_user.id,
        "email": new_user.email,
        "role": new_user.role.value
    })

    return TokenResponse(
        access_token=token,
        user=UserResponse(
            id=new_user.id,
            email=new_user.email,
            full_name=new_user.full_name,
            role=new_user.role
        )
    )


@router.post("/login", response_model=TokenResponse)
@limiter.limit("20/hour")  # Limit login attempts to prevent brute force
def login(request: Request, user: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate user and return token with role information
    """
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Create access token with role
    token = create_access_token({
        "user_id": db_user.id,
        "email": db_user.email,
        "role": db_user.role.value
    })

    return TokenResponse(
        access_token=token,
        user=UserResponse(
            id=db_user.id,
            email=db_user.email,
            full_name=db_user.full_name,
            role=db_user.role
        )
    )