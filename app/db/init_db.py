from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.user import User
from app.core import security
from app.models.company import Company

def init_db(db: Session) -> None:
    # 0. Seed default companies if none exist
    if db.query(Company).count() == 0:
        default_companies = [
            Company(
                id="wysele",
                name="WYSELE",
                domain="wysele.com",
                email_domain="wysele.com",
                description="Wysele Consulting and Recruitment services.",
                domain_link="https://wysele.com",
                responsible_person="System Team",
                address="Wysele Office, Bangalore",
                documents=None
            ),
            Company(
                id="orbintix",
                name="ORBINTIX",
                domain="orbintix.com",
                email_domain="orbintix.com",
                description="Orbintix Tech Solutions.",
                domain_link="https://orbintix.com",
                responsible_person="System Team",
                address="Orbintix Office, Bangalore",
                documents=None
            ),
            Company(
                id="gracevirtue",
                name="GRACE VIRTUE",
                domain="gracevirtue.com",
                email_domain="gracevirtue.com",
                description="Grace Virtue HR and Consulting Services.",
                domain_link="https://gracevirtue.com",
                responsible_person="System Team",
                address="Grace Virtue Office, Bangalore",
                documents=None
            )
        ]
        db.add_all(default_companies)
        db.commit()
        print("[SUCCESS] Default companies (wysele, orbintix, gracevirtue) seeded.")

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