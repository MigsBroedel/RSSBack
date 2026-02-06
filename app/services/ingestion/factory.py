from app.models.source import SourceType
from app.services.ingestion.base import ContentIngestor
from app.services.ingestion.rss import RSSIngestor
from app.services.ingestion.html import HTMLScraperIngestor
from app.services.ingestion.youtube import YouTubeIngestor

class IngestorFactory:
    @staticmethod
    def get_ingestor(source_type: SourceType) -> ContentIngestor:
        if source_type == SourceType.RSS:
            return RSSIngestor()
        elif source_type in [SourceType.SITE_HTML, SourceType.BLOG]:
            return HTMLScraperIngestor()
        elif source_type in [SourceType.YOUTUBE_CHANNEL, SourceType.YOUTUBE_PLAYLIST]:
            return YouTubeIngestor()
        else:
            raise ValueError(f"Unknown source type: {source_type}")
