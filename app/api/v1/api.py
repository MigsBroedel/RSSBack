from fastapi import APIRouter

from app.api.v1.endpoints import auth, sources, feed, users

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(sources.router, prefix="/sources", tags=["sources"])
api_router.include_router(feed.router, prefix="/feed", tags=["feed"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
