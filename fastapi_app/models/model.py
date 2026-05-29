from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime
from uuid import UUID

class TrackModel(BaseModel):
    id: UUID
    name: str
    color: Optional[str] = "#6f1d1b"
    description: Optional[str] = None

class SpeakerModel(BaseModel):
    id: UUID
    name: str

class SessionModel(BaseModel):
    id: UUID
    title: str
    abstract: Optional[str] = None
    starts_at: datetime
    ends_at: datetime
    capacity: Optional[int] = None
    registered: int = 0
    track: Optional[TrackModel] = None
    speakers: List[SpeakerModel] = []
    
    model_config = ConfigDict(from_attributes=True)

class PaginatedSessionResponse(BaseModel):
    count: int
    page: int
    results: List[SessionModel] 