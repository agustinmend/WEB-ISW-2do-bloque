import json
from fastapi import HTTPException
from repositories.session_repo import SessionRepositoryProtocol
from repositories.cache import CacheProtocol

class SessionService:
    def __init__(self, db: SessionRepositoryProtocol, cache: CacheProtocol):
        self.db = db
        self.cache = cache

    def get_paginated_sessions(self, page: int, page_size: int, search: str, track: str, day: str, tz: str) -> dict:
        cache_key = f"sessions:p{page}:s{page_size}:q{search}:t{track}:d{day}:z{tz}"
        cached = self.cache.get_data(cache_key)
        if cached:
            return json.loads(cached)

        offset = (page - 1) * page_size
        total, sessions = self.db.get_sessions(page_size, offset, search, track, day, tz)
        
        for s in sessions:
            s['id'] = str(s['id'])
            s['starts_at'] = s['starts_at'].isoformat()
            s['ends_at'] = s['ends_at'].isoformat()

        result = {"count": total, "page": page, "results": sessions}
        self.cache.set_data(cache_key, json.dumps(result), 60)
        return result

    def get_session_detail(self, session_id: str) -> dict:
        cache_key = f"session_detail:{session_id}"
        cached = self.cache.get_data(cache_key)
        if cached:
            return json.loads(cached)

        session = self.db.get_session_by_id(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session no encontrada")
        
        session['id'] = str(session['id'])
        session['starts_at'] = session['starts_at'].isoformat()
        session['ends_at'] = session['ends_at'].isoformat()
        
        self.cache.set_data(cache_key, json.dumps(session), 60)
        return session
    
    def search_sessions_by_text(self, query: str) -> list:
        return self.db.search_sessions(query)