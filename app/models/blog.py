from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.base_class import Base

class Blog(Base):
    __tablename__ = "blogs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    category = Column(String, index=True)
    image_url = Column(String)
    image_urls = Column(JSON, nullable=True, default=list)
    read_time = Column(String)
    status = Column(String, default="ACTIVE", nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    # Author Info
    author_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    author_name = Column(String, nullable=True)