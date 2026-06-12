from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime, timezone
from app.db.base_class import Base

class ContactInquiry(Base):
    __tablename__ = "contact_inquiries"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone_number = Column(String, nullable=True)
    location = Column(String, nullable=True)
    message = Column(Text, nullable=False)
    company = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
