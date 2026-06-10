from sqlalchemy import Column, Integer, String, Text, Date, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.base_class import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(Text, nullable=False)
    experience = Column(String, nullable=False)
    job_code = Column(String, unique=True, nullable=False, index=True)
    job_posted_date = Column(Date, nullable=False)
    job_type = Column(String, nullable=False)
    key_skills = Column(ARRAY(String), nullable=False)
    responsibilities = Column(ARRAY(String), nullable=True)
    last_date_to_apply = Column(Date, nullable=False)
    location = Column(String, nullable=False)
    region = Column(String, nullable=False)
    role = Column(String, nullable=False)
    salary = Column(String, nullable=True)
    status = Column(String, default="ACTIVE", nullable=False)

    company_id = Column(String, index=True, nullable=True)
    company_name = Column(String, nullable=True)

    posted_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    poster = relationship("User", foreign_keys=[posted_by])

    is_deleted = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    applications = relationship("Application", back_populates="job")
