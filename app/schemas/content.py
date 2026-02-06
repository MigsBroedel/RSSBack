from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime

class ContentItemBase(BaseModel):
    title: str
    url: str
    summary: Optional[str] = None
    image_url: Optional[str] = None
    published_at: Optional[datetime] = None
    content_type: str = "article"

class ContentItemCreate(ContentItemBase):
    source_id: int
    raw_payload: Optional[dict] = {}
    content_hash: str

from app.schemas.source import Source

class ContentItem(ContentItemBase):
    id: int
    source_id: int
    source: Optional[Source] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
