import secrets
import string
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Response, Request
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from app.services import auth_service
from app.services.email_service import send_new_account_email, send_password_reset_email
from app.core import security
from app.core.config import settings
from app.api.deps import get_db, get_current_user, get_current_super_admin
from app.schemas.user import Token, LoginRequest, UserRegister, UserResponse, PasswordChange, PasswordResetRequest, PasswordReset, RefreshTokenRequest
from app.models.user import User, UserToken
from app.services.audit_service import log_audit_event
import uuid

router = APIRouter()


def generate_random_password(length: int = 12) -> str:
    if length < 8:
        length = 12
    # Ensure we get one of each required type
    upper = secrets.choice(string.ascii_uppercase)
    lower = secrets.choice(string.ascii_lowercase)
    digit = secrets.choice(string.digits)
    special = secrets.choice("!@#$%^&*()")
    
    # Fill the remaining characters
    all_chars = string.ascii_letters + string.digits + "!@#$%^&*()"
    remaining = "".join(secrets.choice(all_chars) for _ in range(length - 4))
    
    # Combine and shuffle
    password_list = list(upper + lower + digit + special + remaining)
    secrets.SystemRandom().shuffle(password_list)
    return "".join(password_list)


def generate_tokens(db: Session, user_id: int) -> tuple[str, str]:
    access_token_val = str(uuid.uuid4())
    refresh_token_val = str(uuid.uuid4())
    
    # Store access token
    db_access = UserToken(
        token=access_token_val,
        user_id=user_id,
        token_type="ACCESS",
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    # Store refresh token
    db_refresh = UserToken(
        token=refresh_token_val,
        user_id=user_id,
        token_type="REFRESH",
        expires_at=datetime.now(timezone.utc) + timedelta(days=7)
    )
    db.add(db_access)
    db.add(db_refresh)
    db.commit()
    return access_token_val, refresh_token_val


@router.post("/login", response_model=Token)
def login(credentials: LoginRequest, response: Response, request: Request, db: Session = Depends(get_db)):
    # Find user by email (case-insensitive)
    user = db.query(User).filter(User.email.ilike(credentials.email)).first()
    if not user:
        log_audit_event(
            db,
            action="LOGIN_FAILED",
            email=credentials.email,
            details={"message": "Email doesn't exist"},
            ip_address=request.client.host if request.client else None
        )
        raise HTTPException(status_code=400, detail="Email doesn't exist")

    # Verify password
    from app.core.security import verify_password
    if not verify_password(credentials.password, user.hashed_password):
        log_audit_event(
            db,
            action="LOGIN_FAILED",
            email=credentials.email,
            details={"message": "Incorrect password"},
            ip_address=request.client.host if request.client else None
        )
        raise HTTPException(status_code=400, detail="Incorrect password")

    # Verify role
    if user.role not in ["ADMIN", "SUPER_ADMIN"]:
        log_audit_event(
            db,
            action="LOGIN_FAILED",
            email=credentials.email,
            details={"message": "Unauthorized role"},
            ip_address=request.client.host if request.client else None
        )
        raise HTTPException(status_code=400, detail="Unauthorized role")

    if not user.is_active:
        log_audit_event(
            db,
            action="LOGIN_FAILED",
            user_id=user.id,
            email=user.email,
            details={"message": "Account deactivated"},
            ip_address=request.client.host if request.client else None
        )
        raise HTTPException(status_code=403, detail="Account deactivated")

    # Generate and store UUID tokens in the database
    access_token, refresh_token = generate_tokens(db, user.id)
    is_production = settings.ENVIRONMENT == "production"

    # Always set HttpOnly cookie
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=is_production,
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

    # Log successful login
    log_audit_event(
        db,
        action="LOGIN",
        user_id=user.id,
        email=user.email,
        details={"message": "User logged in successfully"},
        ip_address=request.client.host if request.client else None
    )

    return {
        "token_type": "bearer",
        "role": user.role,
        "is_first_login": user.is_first_login,
        "access_token": access_token,
        "refresh_token": refresh_token,
    }


@router.post("/refresh", response_model=Token)
def refresh(body: RefreshTokenRequest, response: Response, db: Session = Depends(get_db)):
    # Check the database for the active refresh token
    db_refresh = db.query(UserToken).filter(
        UserToken.token == body.refresh_token,
        UserToken.token_type == "REFRESH",
        UserToken.is_active == True
    ).first()

    if not db_refresh:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    expires_at = db_refresh.expires_at
    now = datetime.now(timezone.utc) if expires_at.tzinfo is not None else datetime.utcnow()
    if expires_at < now:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user = db_refresh.user
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    # Invalidate/Deactivate all old tokens for this user
    db.query(UserToken).filter(UserToken.user_id == user.id).update({"is_active": False})
    db.commit()

    # Generate new access/refresh tokens
    new_access_token, new_refresh_token = generate_tokens(db, user.id)
    is_production = settings.ENVIRONMENT == "production"

    response.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=True,
        secure=is_production,
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

    return {
        "token_type": "bearer",
        "role": user.role,
        "is_first_login": user.is_first_login,
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
    }


@router.post("/register", response_model=UserResponse)
def register_user(
    user_in: UserRegister,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_super_admin)
):
    existing = db.query(User.email, User.employee_id).filter(
        (User.email == user_in.email) | (User.employee_id == user_in.emp_id)
    ).first()
    if existing:
        if existing.email == user_in.email:
            raise HTTPException(status_code=400, detail="Email already exists")
        raise HTTPException(status_code=400, detail="Employee ID already exists")

    # Map name to first/last name to prevent DB NULL errors
    names = user_in.name.strip().split(" ", 1)
    first_name = names[0]
    last_name = names[1] if len(names) > 1 else "Admin"

    from app.api.deps import normalize_company
    company_id, company_name = normalize_company(user_in.company_name)

    # Generate random password if not provided
    temp_password = user_in.password or generate_random_password()

    new_user = User(
        employee_id=user_in.emp_id,
        email=user_in.email,
        name=user_in.name,
        first_name=first_name,
        middle_name=None,
        last_name=last_name,
        phone_number=user_in.phone_number,
        company_id=company_id,
        company_name=company_name,
        role=user_in.role,
        hashed_password=security.get_password_hash(temp_password),
        is_active=user_in.is_active,
        is_first_login=True,
        created_by_id=current_user.id
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Log admin creation
    log_audit_event(
        db,
        action="ADMIN_CREATION",
        user_id=current_user.id,
        email=current_user.email,
        details={
            "created_admin_id": new_user.id,
            "created_admin_email": new_user.email,
            "company_name": new_user.company_name,
            "role": new_user.role
        },
        ip_address=request.client.host if request.client else None
    )

    # Send welcome email with login credentials
    background_tasks.add_task(
        send_new_account_email,
        email_to=new_user.email,
        username=new_user.email,
        password=temp_password
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

    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")

    reset_expiry = user.reset_token_expiry
    if reset_expiry:
        now = datetime.now(timezone.utc) if reset_expiry.tzinfo is not None else datetime.utcnow()
        if reset_expiry < now:
            raise HTTPException(status_code=400, detail="Invalid or expired reset token")
    else:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")

    user.hashed_password = security.get_password_hash(body.new_password)
    user.reset_token = None
    user.reset_token_expiry = None
    user.is_first_login = False
    db.commit()
    return {"message": "Password reset successfully"}
