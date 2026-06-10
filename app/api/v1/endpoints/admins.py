from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from app.api.deps import get_db, get_current_super_admin
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate, PermissionsUpdate, UserRegister
from app.services.audit_service import log_audit_event

router = APIRouter()


# GET all admins (SUPER_ADMIN only)
@router.get("/", response_model=List[UserResponse])
def get_all_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_super_admin)
):
    return db.query(User).filter(User.role.in_(["ADMIN", "SUPER_ADMIN"])).order_by(User.created_at.desc()).all()


# POST create new admin (SUPER_ADMIN only)
@router.post("/", response_model=UserResponse)
def create_admin(
    user_in: UserRegister,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_super_admin)
):
    from app.api.v1.endpoints.auth import register_user
    return register_user(user_in, background_tasks, request, db, current_user)


# GET single user (SUPER_ADMIN only)
@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_super_admin)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# UPDATE user details (SUPER_ADMIN only)
@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_in: UserUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_super_admin)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    old_details = {
        "name": user.name,
        "email": user.email,
        "role": user.role,
        "company_name": user.company_name,
        "emp_id": user.employee_id,
        "is_active": user.is_active
    }

    # Map name splitting to first/last name to prevent DB NULL errors
    if user_in.name is not None:
        user.name = user_in.name
        names = user_in.name.strip().split(" ", 1)
        user.first_name = names[0]
        user.last_name = names[1] if len(names) > 1 else "Admin"

    # Map company name to ID
    if user_in.company_name is not None:
        user.company_name = user_in.company_name.upper()
        company_id_map = {
            "WYSELE": "WYSELE",
            "ORBINTIX": "ORBINTIX",
            "GRACE VIRTUE": "GRACE_VIRTUE"
        }
        user.company_id = company_id_map.get(user_in.company_name.upper(), "WYSELE")

    if user_in.emp_id is not None:
        user.employee_id = user_in.emp_id

    # Handle remaining fields
    for field in ["phone_number", "role", "is_active"]:
        val = getattr(user_in, field)
        if val is not None:
            setattr(user, field, val)

    db.commit()
    db.refresh(user)

    new_details = {
        "name": user.name,
        "email": user.email,
        "role": user.role,
        "company_name": user.company_name,
        "emp_id": user.employee_id,
        "is_active": user.is_active
    }

    # Log admin update
    log_audit_event(
        db,
        action="ADMIN_UPDATE",
        user_id=current_user.id,
        email=current_user.email,
        details={
            "target_user_id": user.id,
            "old_details": old_details,
            "new_details": new_details
        },
        ip_address=request.client.host if request.client else None
    )

    return user


# PATCH permissions — control panel (SUPER_ADMIN only)
@router.patch("/{user_id}/permissions", response_model=UserResponse)
def update_permissions(
    user_id: int,
    perms: PermissionsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_super_admin)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    for field, value in perms.model_dump(exclude_unset=True).items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return user


# PATCH activate/deactivate (SUPER_ADMIN only)
@router.patch("/{user_id}/status", response_model=UserResponse)
def toggle_status(
    user_id: int,
    is_active: bool,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_super_admin)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    old_status = user.is_active
    user.is_active = is_active
    db.commit()
    db.refresh(user)

    # Log user status change
    log_audit_event(
        db,
        action="USER_STATUS_CHANGE",
        user_id=current_user.id,
        email=current_user.email,
        details={
            "target_user_id": user.id,
            "target_user_email": user.email,
            "old_status": old_status,
            "new_status": is_active
        },
        ip_address=request.client.host if request.client else None
    )

    return user
