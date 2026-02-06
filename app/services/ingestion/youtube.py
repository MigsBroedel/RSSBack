import feedparser
import asyncio
from typing import List
from datetime import datetime
from time import mktime
from app.services.ingestion.base import ContentIngestor, IngestedItem

class YouTubeIngestor(ContentIngestor):
    async def fetch(self, url: str) -> List[IngestedItem]:
        # Handle Channel vs Playlist
        # URL format: https://www.youtube.com/feeds/videos.xml?channel_id=...
        # or convert channel URL to feed URL if raw URL is passed?
        
        feed_url = url
        # Naive conversion if user provides standard URL
        if "youtube.com/channel/" in url and "feeds" not in url:
            channel_id = url.split("channel/")[-1].split("/")[0]
            feed_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
            
        loop = asyncio.get_event_loop()
        feed = await loop.run_in_executor(None, feedparser.parse, feed_url)
        
        items = []
        for entry in feed.entries:
            # YouTube specific fields
            video_id = entry.yt_videoid if hasattr(entry, 'yt_videoid') else ""
            
            published = None
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                 published = datetime.fromtimestamp(mktime(entry.published_parsed))
            
            # Thumbnail is usually in media_group
            image_url = None
            if "media_thumbnail" in entry:
                image_url = entry.media_thumbnail[0]["url"]
            elif "media_group" in entry and len(entry.media_group) > 0:
                 thumbs = entry.media_group[0].get("media_thumbnail", [])
                 if thumbs:
                     image_url = thumbs[0]["url"]

            items.append(IngestedItem(
                title=entry.get("title", ""),
                url=entry.get("link", ""),
                summary=entry.get("summary", ""), # Description
                published_at=published,
                image_url=image_url,
                raw_payload=dict(entry),
                content_type="video"
            ))
        return items
