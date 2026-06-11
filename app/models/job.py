from sqlalchemy import Column, Integer, String, Text, Date, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.base_class import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    job_code = Column(String, unique=True, nullable=False, index=True)
    company_name = Column(String, nullable=False)
    job_title = Column(String, nullable=False)
    department = Column(String, nullable=False)
    employment_type = Column(String, nullable=False)
    work_mode = Column(String, nullable=False)
    experience = Column(String, nullable=False)
    openings = Column(Integer, nullable=False)
    location = Column(String, nullable=False)
    min_salary = Column(Integer, nullable=True)
    max_salary = Column(Integer, nullable=True)
    description = Column(Text, nullable=False)
    responsibilities = Column(ARRAY(String), nullable=True)
    required_skills = Column(ARRAY(String), nullable=False)
    qualification = Column(String, nullable=True)
    application_email = Column(String, nullable=True)
    application_deadline = Column(Date, nullable=False)
    job_posted_date = Column(Date, default=lambda: datetime.utcnow().date())
    role = Column(String, nullable=False)
    status = Column(String, default="ACTIVE", nullable=False)

    company_id = Column(String, index=True, nullable=True)
    company_name = Column(String, nullable=True)

    posted_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    poster = relationship("User", foreign_keys=[posted_by])

    is_deleted = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    applications = relationship("Application", back_populates="job")
