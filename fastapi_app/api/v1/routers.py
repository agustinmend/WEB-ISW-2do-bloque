from fastapi import APIRouter
from . import tracks, sessions

router = APIRouter()

router.include_router(tracks.router)
router.include_router(sessions.router)