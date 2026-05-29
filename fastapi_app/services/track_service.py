import json
from typing import List
from repositories.track_repo import TrackRepositoryProtocol
from repositories.cache import CacheProtocol

class TrackService:
    def __init__(self, db: TrackRepositoryProtocol, cache: CacheProtocol):
        self.db = db
        self.cache = cache

    def get_all_tracks(self) -> List[dict]:
        cached = self.cache.get_data("api:tracks")
        if cached:
            return json.loads(cached)
        
        tracks = self.db.get_tracks()
        for t in tracks:
            t['id'] = str(t['id'])
            
        self.cache.set_data("api:tracks", json.dumps(tracks), 60)
        return tracks