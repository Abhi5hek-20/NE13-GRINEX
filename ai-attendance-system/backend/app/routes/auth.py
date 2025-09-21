from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List

from ..models import get_db, User, Token, UserLogin, UserCreate, UserResponse
from ..utils.auth import authenticate_user, create_access_token, get_password_hash, ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter()

@router.post("/login", response_model=Token)
async def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """Authenticate user and return access token."""
    user = authenticate_user(db, user_credentials.email, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_type": user.user_type,
        "user_id": user.id
    }

@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user (lecturer or student)."""
    # Check if user already exists
    db_user = db.query(User).filter(User.email == user_data.email).first()
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    # Check if employee_id or student_id already exists
    if user_data.employee_id:
        existing_employee = db.query(User).filter(User.employee_id == user_data.employee_id).first()
        if existing_employee:
            raise HTTPException(
                status_code=400,
                detail="Employee ID already exists"
            )
    
    if user_data.student_id:
        existing_student = db.query(User).filter(User.student_id == user_data.student_id).first()
        if existing_student:
            raise HTTPException(
                status_code=400,
                detail="Student ID already exists"
            )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        user_type=user_data.user_type,
        employee_id=user_data.employee_id,
        student_id=user_data.student_id,
        department=user_data.department
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

@router.get("/users", response_model=List[UserResponse])
async def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get list of users (for admin purposes)."""
    users = db.query(User).offset(skip).limit(limit).all()
    return users