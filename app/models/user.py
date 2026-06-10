from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    first_name = Column(String, nullable=False)
    middle_name = Column(String, nullable=True)
    last_name = Column(String, nullable=False)
    phone_number = Column(String, nullable=True)
    name = Column(String, nullable=True)

    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_first_login = Column(Boolean, default=True)
    role = Column(String, default="ADMIN")

    company_id = Column(String, nullable=True)
    company_name = Column(String, nullable=True)

    # Blog permissions
    can_post_blog = Column(Boolean, default=False)
    can_edit_blog = Column(Boolean, default=False)
    can_delete_blog = Column(Boolean, default=False)

    # HR permissions
    can_post_job = Column(Boolean, default=False)

    # Admin access permissions
    can_access_contact = Column(Boolean, default=False)
    can_access_consulting = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    reset_token = Column(String, nullable=True)
    reset_token_expiry = Column(DateTime(timezone=True), nullable=True)

    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    creator = relationship("User", remote_side=[id], backref="created_users")

    @property
    def emp_id(self) -> str:
        return self.employee_id

    @emp_id.setter
    def emp_id(self, value: str):
        self.employee_id = value
