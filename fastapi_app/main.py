from fastapi import FastAPI, Depends, Response
from api.v1.routers import router as api_router
from repositories.session_repo import SessionRepositoryProtocol, PostgresSessionRepository
from repositories.cache import CacheProtocol, RedisCache

app = FastAPI(title="Symposium API")
app.include_router(api_router, prefix="/api/v1")

@app.get("/api/v1/healthz")
def health_check(response: Response, db: SessionRepositoryProtocol = Depends(PostgresSessionRepository), cache: CacheProtocol = Depends(RedisCache)):
    status_data = {"status": "ok", "checks": {"postgres": "ok", "redis": "ok"}}
    try:
        with db._connect() as conn:
            conn.cursor().execute("SELECT 1")
    except Exception:
        status_data["checks"]["postgres"] = "error"
        status_data["status"] = "error"
        response.status_code = 503
        
    try:
        cache.client.ping()
    except Exception:
        status_data["checks"]["redis"] = "error"

    return status_data