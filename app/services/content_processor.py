import hashlib
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timezone

from app.models.source import Source
from app.models.content import ContentItem
from app.services.ingestion.factory import IngestorFactory
from app.schemas.content import ContentItemCreate

class ContentProcessor:
    def __init__(self, db: AsyncSession):
        self.db = db

    def generate_hash(self, title: str, url: str) -> str:
        s = f"{title}{url}".encode('utf-8')
        return hashlib.sha256(s).hexdigest()

    async def process_source(self, source_id: int):
        result = await self.db.execute(select(Source).where(Source.id == source_id))
        source = result.scalars().first()
        if not source:
            return

        ingestor = IngestorFactory.get_ingestor(source.type)
        try:
            items = await ingestor.fetch(source.url)
            
            new_items_count = 0
            for item in items:
                content_hash = self.generate_hash(item.title, item.url)
                
                # Check for duplicate
                # Optimized: We could batch check, but for MVP loop is fine with index
                # Ideally we check existence first to save DB bandwidth on writes
                
                # Check existance
                q = select(ContentItem).where(ContentItem.content_hash == content_hash)
                existing = await self.db.execute(q)
                if existing.scalars().first():
                    continue

                new_content = ContentItem(
                    source_id=source.id,
                    title=item.title,
                    url=item.url,
                    summary=item.summary,
                    image_url=item.image_url,
                    published_at=item.published_at or datetime.now(timezone.utc),
                    content_type=item.content_type,
                    raw_payload=item.raw_payload,
                    content_hash=content_hash
                )
                self.db.add(new_content)
                new_items_count += 1
            
            source.last_fetch = datetime.now(timezone.utc)
            source.error_count = 0 # Reset error count on success
            await self.db.commit()
            return new_items_count

        except Exception as e:
            # Log error
            print(f"Error fetching source {source.id}: {e}")
            source.error_count += 1
            await self.db.commit()
            raise e
