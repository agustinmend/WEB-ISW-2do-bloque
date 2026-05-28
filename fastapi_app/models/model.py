from pydantic import BaseModel, Field
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
    affiliation: Optional[str] = None

class SessionModel(BaseModel):
    id: UUID
    title: str
    abstract: Optional[str] = None
    starts_at: datetime
    ends_at: datetime
    capacity: int
    registered: int
    track: Optional[TrackModel] = None
    speakers: List[SpeakerModel] = []

class PaginatedSessionResponse(BaseModel):
    count: int
    page: int
    results: List[SessionModel] 