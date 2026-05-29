from fastapi import HTTPException
from repositories.session_repo import SessionRepositoryProtocol

class SessionService:
    def __init__(self, db: SessionRepositoryProtocol):
        self.db = db

    def get_paginated_sessions(self, page: int, page_size: int, search: str, track: str, day: str, tz: str) -> dict:
        offset = (page - 1) * page_size
        total, sessions = self.db.get_sessions(page_size, offset, search, track, day, tz)
        return {"count": total, "page": page, "results": sessions}
    
    def get_session_detail(self, session_id: str) -> dict:
        session = self.db.get_session_by_id(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session no encontrada")
        return session