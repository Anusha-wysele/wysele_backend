from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey
from datetime import datetime
from app.db.base_class import Base

class Audit(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    email = Column(String, nullable=True)
    action = Column(String, nullable=False)
    details = Column(JSON, nullable=True)
    ip_address = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)