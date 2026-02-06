import asyncio
from app.workers.celery_app import celery_app
from app.db.session import SessionLocal
from app.services.content_processor import ContentProcessor
from app.models.source import Source
from sqlalchemy.future import select
from datetime import datetime, timezone, timedelta

@celery_app.task
def fetch_source_task(source_id: int):
    async def _process():
        async with SessionLocal() as db:
            processor = ContentProcessor(db)
            await processor.process_source(source_id)
            
    try:
        asyncio.run(_process())
    except Exception as e:
        print(f"Task failed: {e}")

@celery_app.task
def schedule_feeds_update():
    async def _schedule():
        async with SessionLocal() as db:
            stmt = select(Source).where(Source.is_active == True)
            result = await db.execute(stmt)
            sources = result.scalars().all()
            
            now = datetime.now(timezone.utc)
            for source in sources:
                # Check interval
                should_update = False
                if not source.last_fetch:
                    should_update = True
                else:
                    delta = now - source.last_fetch
                    if delta.total_seconds() / 60 >= source.update_interval_minutes:
                        should_update = True
                
                if should_update:
                    fetch_source_task.delay(source.id)
                
    try:
        asyncio.run(_schedule())
    except Exception as e:
        print(f"Scheduler failed: {e}")

celery_app.conf.beat_schedule = {
    "update-feeds-every-minute": {
        "task": "app.workers.tasks.schedule_feeds_update",
        "schedule": 60.0,
    }
}
