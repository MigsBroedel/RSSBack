from typing import Any, List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc

from app.api import deps
from app.models.user import User
from app.models.source import Source
from app.models.content import ContentItem
from app.schemas.content import ContentItem as ContentSchema

from sqlalchemy.orm import selectinload

router = APIRouter()

@router.get("/", response_model=List[ContentSchema])
async def read_feed(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    skip: int = 0,
    limit: int = 50,
    source_id: Optional[int] = None,
    content_type: Optional[str] = None
) -> Any:
    # Select content items from sources the user follows
    
    stmt = select(ContentItem).join(Source).join(Source.users).where(User.id == current_user.id)
    
    if source_id:
        stmt = stmt.where(ContentItem.source_id == source_id)
    
    if content_type:
        stmt = stmt.where(ContentItem.content_type == content_type)
        
    stmt = stmt.options(selectinload(ContentItem.source))
    stmt = stmt.order_by(desc(ContentItem.published_at)).offset(skip).limit(limit)
    
    result = await db.execute(stmt)
    return result.scalars().all()
