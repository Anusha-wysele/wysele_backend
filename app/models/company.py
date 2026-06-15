from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.db.base_class import Base

class Company(Base):
    __tablename__ = "companies"

    id = Column(String, primary_key=True, index=True) # lowercase identifier, e.g. 'wysele'
    name = Column(String, nullable=False)
    domain = Column(String, nullable=False)
    email_domain = Column(String, nullable=False)
    description = Column(String, nullable=False)
    domain_link = Column(String, nullable=False)
    responsible_person = Column(String, nullable=False)
    documents = Column(String, nullable=True) # Optional documents list or URL
    address = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
