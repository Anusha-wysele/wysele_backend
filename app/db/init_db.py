from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.user import User
from app.core import security

def init_db(db: Session) -> None:
    # 1. Search for the user defined in your .env
    user = db.query(User).filter(User.email == settings.FIRST_SUPERUSER).first()
    
    # 2. If they don't exist (fresh database), create them
    if not user:
        root_user = User(
            email=settings.FIRST_SUPERUSER,
            hashed_password=security.get_password_hash(settings.FIRST_SUPERUSER_PASSWORD),
            first_name="Root",
            last_name="Admin",
            role="SUPER_ADMIN",
            is_active=True,
            can_post_blog=True,
            can_edit_blog=True,
            # --- ADD THESE TWO LINES ---
            employee_id="ROOT001",  # A unique ID for your first user
            company_id="WYSELE"     # A default company string
            # ---------------------------
        )
        db.add(root_user)
        db.commit()
        db.refresh(root_user)
        print(f"[SUCCESS] Root Admin '{settings.FIRST_SUPERUSER}' initialized.")
    else:
        print(f"[INFO] Root Admin '{settings.FIRST_SUPERUSER}' already exists. Skipping init.")