from fastapi import APIRouter, Depends, Query
from repositories.session_repo import SessionRepositoryProtocol, PostgresSessionRepository
from services.session_service import SessionService
from models.session import PaginatedSessionResponse

router = APIRouter(prefix="/sessions", tags=["Sessions"])

def get_session_db() -> SessionRepositoryProtocol:
    return PostgresSessionRepository()

def get_session_service(db: SessionRepositoryProtocol = Depends(get_session_db)) -> SessionService:
    return SessionService(db)

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