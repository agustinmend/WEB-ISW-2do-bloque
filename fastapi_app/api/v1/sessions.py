from fastapi import APIRouter, Depends, Query
from uuid import UUID
from repositories.session_repo import SessionRepositoryProtocol, PostgresSessionRepository
from services.session_service import SessionService
from models.model import PaginatedSessionResponse, SessionModel
from typing import List
from repositories.cache import RedisCache, CacheProtocol

router = APIRouter(prefix="/sessions", tags=["Sessions"])

def get_session_db() -> SessionRepositoryProtocol:
    return PostgresSessionRepository()

def get_cache() -> CacheProtocol:
    return RedisCache()

def get_session_service(
    db: SessionRepositoryProtocol = Depends(get_session_db), 
    cache: CacheProtocol = Depends(get_cache)
) -> SessionService:
    return SessionService(db, cache)

@router.get("/", response_model=PaginatedSessionResponse)
def list_sessions(
    q: str = Query("", description="Texto de búsqueda"),
    track: str = Query("", description="ID del track"),
    day: str = Query("", description="Día YYYY-MM-DD"),
    tz: str = Query("UTC", description="Zona horaria"),
    page: int = Query(1, ge=1),
    page_size: int = Query(12, ge=1, le=50),
    service: SessionService = Depends(get_session_service)
):
    return service.get_paginated_sessions(page, page_size, q, track, day, tz)

@router.get("/search/", response_model=List[SessionModel])
def search_sessions(
    query: str = Query(..., description="Texto a buscar"),
    service: SessionService = Depends(get_session_service)
):
    return service.search_sessions_by_text(query)

@router.get("/{session_id}", response_model=SessionModel)
def get_session(session_id: UUID, service: SessionService = Depends(get_session_service)):
    return service.get_session_detail(str(session_id))