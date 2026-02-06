from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api import deps
from app.models.user import User
from app.models.source import Source, SourceType
from app.schemas.source import Source as SourceSchema, SourceCreate
from app.services.content_processor import ContentProcessor

router = APIRouter()

@router.get("/", response_model=List[SourceSchema])
async def read_sources(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    skip: int = 0,
    limit: int = 100
) -> Any:
    # Get sources for current user
    # Since we have a many-to-many, we need to join
    # Async SQL is tricky with relationships if not loaded eagerly.
    # But let's assume we want to list ALL sources the user is subscribed to.
    
    # We can use the relation... 
    # But await current_user.awaitable_attrs.sources is required if loose
    # Let's use direct query
    
    stmt = select(Source).join(Source.users).where(User.id == current_user.id).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()

@router.post("/", response_model=SourceSchema)
async def create_source(
    *,
    db: AsyncSession = Depends(deps.get_db),
    source_in: SourceCreate,
    current_user: User = Depends(deps.get_current_user),
    background_tasks: BackgroundTasks
) -> Any:
    # Check if source exists globally by URL
    stmt = select(Source).where(Source.url == source_in.url)
    result = await db.execute(stmt)
    source = result.scalars().first()

    if not source:
        source = Source(
            url=source_in.url,
            name=source_in.name,
            type=source_in.type,
            update_interval_minutes=source_in.update_interval_minutes
        )
        db.add(source)
        await db.commit()
        await db.refresh(source)
        
        # Trigger initial fetch
        processor = ContentProcessor(db)
        # Note: We can't easily pass async db session to background task if it closes.
        # But for 'BackgroundTasks' in FastAPI, it runs after response but before session close? 
        # Actually session might be closed. Better to trigger a logical separate task or handle it here if quick.
        # In production use Celery. For now, let's try await immediately or leave for scheduler.
        # Let's just create it. The scheduler will pick it up or user can trigger manual refresh.

    # Subscribe user to source if not already
    # Re-query to be safe for relationship handling
    # Check if user is already associated (Manual query on association table would be best)
    # But using ORM:
    
    # We need to manually insert into association table if using basic async logic without eager loading tricks
    # Or just use the model manipulation
    
    # Check association
    # This is slightly complex in async sqlalchemy 1.4+ without helper methods
    # Simplest:
    # insert into user_source values ...
    
    # But wait, checking if source is in current_user.sources needs async loading.
    
    # Let's check relation existence query
    # "is this source associated with this user?"
    # q = select(User).where(User.id==user.id).where(User.sources.contains(source)) -- not direct
    
    stmt = select(Source).join(Source.users).where(User.id == current_user.id).where(Source.id == source.id)
    result = await db.execute(stmt)
    if not result.scalars().first():
        # Add association
        # Need to append. 
        # await db.execute(user_source.insert().values(user_id=current_user.id, source_id=source.id)) -- if we have the table object imported
        # Let's import the table object from models.user
        from app.models.user import user_source
        from sqlalchemy import insert
        await db.execute(insert(user_source).values(user_id=current_user.id, source_id=source.id))
        await db.commit()
        
    return source

@router.post("/{source_id}/refresh", response_model=Any)
async def refresh_source(
    source_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    processor = ContentProcessor(db)
    count = await processor.process_source(source_id)
    return {"message": "Source refreshed", "new_items": count}
