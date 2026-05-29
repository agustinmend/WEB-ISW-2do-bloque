from fastapi import APIRouter, Depends
from typing import List
from repositories.track_repo import TrackRepositoryProtocol, PostgresTrackRepository
from repositories.cache import CacheProtocol, RedisCache
from services.track_service import TrackService
from models.model import TrackModel

router = APIRouter(prefix="/tracks", tags=["Tracks"])

def get_track_db() -> TrackRepositoryProtocol:
    return PostgresTrackRepository()
    
def get_cache() -> CacheProtocol:
    return RedisCache()

def get_track_service(db: TrackRepositoryProtocol = Depends(get_track_db), cache: CacheProtocol = Depends(get_cache)) -> TrackService:
    return TrackService(db, cache)

@router.get("/", response_model=List[TrackModel])
def list_tracks(service: TrackService = Depends(get_track_service)):
    return service.get_all_tracks()