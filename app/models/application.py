from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.base_class import Base


class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, nullable=False, index=True)
    mobile_number = Column(String, nullable=False)
    current_location = Column(String, nullable=False)
    region = Column(String, nullable=True)
    current_ctc = Column(String, nullable=True)
    expected_ctc = Column(String, nullable=True)
    notice_period = Column(String, nullable=False)
    relevant_experience = Column(String, nullable=False)
    resume_url = Column(String, nullable=False)
    applied_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    job = relationship("Job", back_populates="applications")

    __table_args__ = (
        UniqueConstraint("job_id", "email", name="uq_job_applicant"),
    )
