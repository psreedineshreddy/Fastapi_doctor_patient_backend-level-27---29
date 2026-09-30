from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.auth import RegisterRequest, LoginRequest
from app.auth.security import hash_password, verify_password
from app.auth.jwt import create_token

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register")
def register(user: RegisterRequest, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(
        email=user.email,
        password_hash=hash_password(user.password),
        role=user.role
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User registered successfully"}


@router.post("/login")
def login(
    username: str = Form(),
    password: str = Form(),
    db: Session = Depends(get_db)
):
    existing_user = db.query(User).filter(User.email == username).first()

    if not existing_user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not verify_password(password, existing_user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_token(existing_user.email, existing_user.role)

    return {
        "access_token": token,
        "token_type": "bearer"
    }