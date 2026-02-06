from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

class IngestedItem(BaseModel):
    title: str
    url: str
    summary: Optional[str] = None
    image_url: Optional[str] = None
    published_at: Optional[datetime] = None
    raw_payload: dict = {}
    content_type: str = "article"

class ContentIngestor(ABC):
    @abstractmethod
    async def fetch(self, url: str) -> List[IngestedItem]:
        pass
