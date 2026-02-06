import enum
from sqlalchemy import Column, Integer, String, Boolean, DateTime, func, Enum, Text
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class SourceType(str, enum.Enum):
    RSS = "RSS"
    SITE_HTML = "SITE_HTML"
    BLOG = "BLOG"
    YOUTUBE_CHANNEL = "YOUTUBE_CHANNEL"
    YOUTUBE_PLAYLIST = "YOUTUBE_PLAYLIST"

class Source(Base):
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, unique=True, index=True, nullable=False)
    name = Column(String)
    type = Column(Enum(SourceType), nullable=False)
    is_active = Column(Boolean, default=True)
    
    last_fetch = Column(DateTime(timezone=True), nullable=True)
    update_interval_minutes = Column(Integer, default=60)
    error_count = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Referencing User via string to avoid circular imports, but secondary needs to be resolvable.
    # Since they share Base, it works if mapped.
    users = relationship("User", secondary="user_source", back_populates="sources")
    contents = relationship("ContentItem", back_populates="source")
