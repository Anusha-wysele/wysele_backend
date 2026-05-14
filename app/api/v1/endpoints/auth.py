import secrets
import string
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from app.services import auth_service
from app.services.email_service import send_new_account_email, send_password_reset_email
from app.core import security
from app.api.deps import get_db, get_current_user, get_current_super_admin
from app.schemas.user import Token, LoginRequest, UserRegister, UserResponse, PasswordChange, PasswordResetRequest, PasswordReset
from app.models.user import User

router = APIRouter()


def generate_random_password(length: int = 12) -> str:
    chars = string.ascii_letters + string.digits + "!@#$%"
    return "".join(secrets.choice(chars) for _ in range(length))


@router.post("/login", response_model=Token)
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    user = auth_service.authenticate(db, email=credentials.email, password=credentials.password)

    if not user or user.role not in ["ADMIN", "SUPER_ADMIN", "HR"]:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account deactivated")

    access_token = security.create_access_token(data={"sub": user.email})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user.role,
        "is_first_login": user.is_first_login,
    }


@router.post("/register", response_model=UserResponse)
def register_user(
    user_in: UserRegister,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_super_admin)
):
    if db.query(User).filter(User.email == user_in.email).first():
        raise HTTPException(status_code=400, detail="Email already exists")

    if db.query(User).filter(User.employee_id == user_in.employee_id).first():
        raise HTTPException(status_code=400, detail="Employee ID already exists")

    # Generate random password — never exposed in API response
    random_password = generate_random_password()

    new_user = User(
        employee_id=user_in.employee_id,
        email=user_in.email,
        first_name=user_in.first_name,
        middle_name=user_in.middle_name,
        last_name=user_in.last_name,
        phone_number=user_in.phone_number,
        company_id=user_in.company_id,
        role=user_in.role,
        hashed_password=security.get_password_hash(random_password),
        is_active=True,
        is_first_login=True,
        created_by_id=current_user.id
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Send password to user email in background
    background_tasks.add_task(
        send_new_account_email,
        email_to=new_user.email,
        username=new_user.email,
        password=random_password
    )

    return new_user


@router.get("/me", response_model=UserResponse)
def read_user_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.patch("/change-password")
def change_password(
    body: PasswordChange,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not security.verify_password(body.old_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Old password is incorrect")

    current_user.hashed_password = security.get_password_hash(body.new_password)
    # Mark first login as complete
    current_user.is_first_login = False
    db.commit()
    return {"message": "Password updated successfully"}


@router.post("/forgot-password")
def forgot_password(
    body: PasswordResetRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == body.email).first()
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
    user = db.query(User).filter(User.reset_token == body.token).first()

    if not user or user.reset_token_expiry < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")

    user.hashed_password = security.get_password_hash(body.new_password)
    user.reset_token = None
    user.reset_token_expiry = None
    user.is_first_login = False
    db.commit()
    return {"message": "Password reset successfully"}
