import feedparser
import asyncio
from typing import List
from datetime import datetime
from time import mktime
from app.services.ingestion.base import ContentIngestor, IngestedItem

class RSSIngestor(ContentIngestor):
    async def fetch(self, url: str) -> List[IngestedItem]:
        # feedparser is blocking, run in executor
        loop = asyncio.get_event_loop()
        feed = await loop.run_in_executor(None, feedparser.parse, url)
        
        items = []
        for entry in feed.entries:
            published = None
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                 published = datetime.fromtimestamp(mktime(entry.published_parsed))
            elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
                 published = datetime.fromtimestamp(mktime(entry.updated_parsed))
            
            image_url = None
            # Basic image extraction heuristic for RSS
            if "media_content" in entry:
                image_url = entry.media_content[0].get("url")
            elif "image" in entry:
                image_url = entry.image.get("href")

            items.append(IngestedItem(
                title=entry.get("title", "No Title"),
                url=entry.get("link", ""),
                summary=entry.get("summary", "") or entry.get("description", ""),
                published_at=published,
                image_url=image_url,
                raw_payload=dict(entry),
                content_type="article"
            ))
        return items
