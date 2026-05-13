from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
import secrets
from app.api import deps
from app.services import auth_service
from app.services.email_service import send_new_account_email, send_password_reset_email
from app.core import security
from app.api.deps import get_db
from app.schemas.user import Token, LoginRequest, UserCreate, UserResponse, PasswordChange, PasswordResetRequest, PasswordReset
from app.models.user import User

router = APIRouter()

@router.post("/login", response_model=Token)
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    user = auth_service.authenticate(db, email=credentials.email, password=credentials.password)

    if not user or user.role not in ["ADMIN", "SUPER_ADMIN"]:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account deactivated")

    access_token = security.create_access_token(data={"sub": user.email})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user.role,
    }

@router.post("/register-admin", response_model=UserResponse)
def register_new_admin(
    user_in: UserCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    if db.query(User).filter(User.email == user_in.email).first():
        raise HTTPException(status_code=400, detail="Email already exists")

    if db.query(User).filter(User.employee_id == user_in.employee_id).first():
        raise HTTPException(status_code=400, detail="Employee ID already exists")

    if user_in.role not in ["ADMIN", "HR"]:
        raise HTTPException(status_code=400, detail="Role must be ADMIN or HR")

    new_user = User(
        email=user_in.email,
        employee_id=user_in.employee_id,
        hashed_password=security.get_password_hash(user_in.password),
        first_name=user_in.first_name,
        middle_name=user_in.middle_name,
        last_name=user_in.last_name,
        phone_number=user_in.phone_number,
        role=user_in.role,
        company_id=user_in.company_id,
        is_active=True,
        created_by_id=None
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    background_tasks.add_task(
        send_new_account_email,
        email_to=new_user.email,
        username=new_user.email,
        password=user_in.password
    )

    return new_user

@router.get("/me", response_model=UserResponse)
def read_user_me(db: Session = Depends(get_db)):
    return db.query(User).filter(User.is_active == True).first()

@router.patch("/change-password")
def change_password(
    body: PasswordChange,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.is_active == True).first()
    if not user or not security.verify_password(body.old_password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Old password is incorrect")
    user.hashed_password = security.get_password_hash(body.new_password)
    db.commit()
    return {"message": "Password updated successfully"}

@router.post("/forgot-password")
def forgot_password(
    body: PasswordResetRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Sends a password reset link to the user's email.
    """
    user = db.query(User).filter(User.email == body.email).first()
    # Always return 200 to avoid email enumeration
    if not user:
        return {"message": "If this email exists, a reset link has been sent"}

    reset_token = secrets.token_urlsafe(32)
    user.reset_token = reset_token
    user.reset_token_expiry = datetime.now(timezone.utc) + timedelta(minutes=30)
    db.commit()

    background_tasks.add_task(send_password_reset_email, email_to=user.email, reset_token=reset_token)
    return {"message": "If this email exists, a reset link has been sent"}

@router.post("/reset-password")
def reset_password(body: PasswordReset, db: Session = Depends(get_db)):
    """
    Resets password using the token received via email.
    """
    user = db.query(User).filter(User.reset_token == body.token).first()

    if not user or user.reset_token_expiry < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")

    user.hashed_password = security.get_password_hash(body.new_password)
    user.reset_token = None
    user.reset_token_expiry = None
    db.commit()
    return {"message": "Password reset successfully"}
