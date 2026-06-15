from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.user import User
from app.core import security
from app.models.company import Company

def init_db(db: Session) -> None:
    # 0. Seed default company (WYSELE) if none exist
    if db.query(Company).count() == 0:
        default_company = Company(
            id="wysele",
            company_name="WYSELE",
            company_type="Pvt Ltd",
            company_email="contact@wysele.com",
            description="Wysele Consulting and Recruitment services.",
            website_url="https://wysele.com",
            company_representative="System Team",
            address="Wysele Office, Bangalore",
            documents=None,
            is_active=True
        )
        db.add(default_company)
        db.commit()
        print("[SUCCESS] Default company (wysele) seeded.")

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