from fastapi import FastAPI
from api.v1.routers import router as api_router

app = FastAPI(title="Symposium API")

app.include_router(api_router, prefix="/api/v1")

@app.get("/api/v1/healthz")
def health_check():
    return {"status": "ok"}