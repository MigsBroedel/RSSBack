from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.source import SourceType

class SourceBase(BaseModel):
    url: str
    name: Optional[str] = None
    type: SourceType = SourceType.RSS
    update_interval_minutes: int = 60

class SourceCreate(SourceBase):
    pass

class SourceUpdate(SourceBase):
    is_active: Optional[bool] = None

class Source(SourceBase):
    id: int
    is_active: bool
    last_fetch: Optional[datetime]
    error_count: int
    created_at: datetime

    class Config:
        from_attributes = True
