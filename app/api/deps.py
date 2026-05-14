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
    # 1. Manually get the Authorization header
    auth_header = request.headers.get("Authorization")
    
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header",
        )

    # 2. Extract the token
    token = auth_header.split(" ")[1]
    
    # 3. Verify the JWT
    email = decode_access_token(token)
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

    # 4. Find the user in DB
    user = db.query(User).filter(User.email == email).first()
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
    if current_user.role not in ["ADMIN", "SUPER_ADMIN", "HR"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="HR or Admin privileges required",
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