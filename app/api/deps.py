from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.core.security import decode_access_token
from app.models.user import User

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
) -> User:
    # 1. Try HttpOnly cookie first
    token = request.cookies.get("access_token")

    # 2. Fallback to Authorization header (for Swagger/testing)
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    # 3. Verify the JWT
    user_id = decode_access_token(token)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

    # 4. Find the user in DB by primary key — fastest possible lookup
    user = db.get(User, int(user_id))
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    return user

def get_current_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Dependency to ensure the current user has ADMIN or SUPER_ADMIN privileges.
    """
    if current_user.role not in ["ADMIN", "SUPER_ADMIN"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return current_user

def get_current_super_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role != "SUPER_ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super admin privileges required",
        )
    return current_user

def get_current_hr_or_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role not in ["ADMIN", "SUPER_ADMIN"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return current_user

def require_can_post_blog(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role == "SUPER_ADMIN":
        return current_user
    if not current_user.can_post_blog:
        raise HTTPException(status_code=403, detail="You do not have permission to post blogs")
    return current_user

def require_can_edit_blog(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role == "SUPER_ADMIN":
        return current_user
    if not current_user.can_edit_blog:
        raise HTTPException(status_code=403, detail="You do not have permission to edit blogs")
    return current_user

def require_can_delete_blog(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role == "SUPER_ADMIN":
        return current_user
    if not current_user.can_delete_blog:
        raise HTTPException(status_code=403, detail="You do not have permission to delete blogs")
    return current_user

def require_can_post_job(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role == "SUPER_ADMIN":
        return current_user
    if not current_user.can_post_job:
        raise HTTPException(status_code=403, detail="You do not have permission to post jobs")
    return current_user

def require_can_access_contact(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role == "SUPER_ADMIN":
        return current_user
    if not current_user.can_access_contact:
        raise HTTPException(status_code=403, detail="You do not have permission to access contacts")
    return current_user

def require_can_access_consulting(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role == "SUPER_ADMIN":
        return current_user
    if not current_user.can_access_consulting:
        raise HTTPException(status_code=403, detail="You do not have permission to access consulting")
    return current_user