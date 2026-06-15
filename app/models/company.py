from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.db.base_class import Base

class Company(Base):
    __tablename__ = "companies"

    id = Column(String, primary_key=True, index=True) # lowercase identifier, e.g. 'wysele'
    company_name = Column(String, nullable=False)
    company_type = Column(String, nullable=False)
    company_email = Column(String, nullable=False)
    description = Column(String, nullable=False)
    website_url = Column(String, nullable=False)
    company_representative = Column(String, nullable=False)
    documents = Column(String, nullable=True) # Optional documents list or URL
    address = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
