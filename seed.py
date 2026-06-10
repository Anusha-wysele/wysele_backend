import sys
import os

# Add current directory to path so it can find 'app'
sys.path.append(os.getcwd())

from app.db.session import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash

def seed_data():
    db = SessionLocal()
    try:
        # Create the Root Super Admin
        admin_email = "admin@wysele.com"
        admin = db.query(User).filter(User.email == admin_email).first()
        
        if not admin:
            # Updated to match the database schema requirements
            admin = User(
                email=admin_email,
                employee_id="ROOT001",
                hashed_password=get_password_hash("admin123"),
                first_name="System",
                middle_name=None,
                last_name="Admin",
                role="ADMIN", # This user acts as the Super Admin via config.py
                company_id="WYSELE",
                is_active=True
            )
            db.add(admin)
            db.commit()
            print("Root Admin created successfully: admin@wysele.com")
        else:
            print("Admin already exists in database.")

    except Exception as e:
        print(f"Error seeding data: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()