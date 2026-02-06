from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class ContentItem(Base):
    __tablename__ = "content_item"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("source.id"), nullable=False)
    
    title = Column(String, nullable=False)
    summary = Column(Text, nullable=True)
    url = Column(String, nullable=False)
    image_url = Column(String, nullable=True)
    
    published_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    content_type = Column(String) # article, video, post
    raw_payload = Column(JSON, nullable=True)
    
    content_hash = Column(String, unique=True, index=True)
    
    source = relationship("Source", back_populates="contents")
