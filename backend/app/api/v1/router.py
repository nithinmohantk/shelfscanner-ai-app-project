from fastapi import APIRouter

from app.api.v1.endpoints import sessions, preferences, scan, recommend, books

api_router = APIRouter()

api_router.include_router(sessions.router, prefix="/sessions", tags=["sessions"])
api_router.include_router(preferences.router, prefix="/preferences", tags=["preferences"])
api_router.include_router(scan.router, prefix="/scan", tags=["scan"])
api_router.include_router(recommend.router, prefix="/recommend", tags=["recommend"])
api_router.include_router(books.router, prefix="/books", tags=["books"])
