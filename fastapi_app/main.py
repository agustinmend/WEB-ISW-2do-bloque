from fastapi import FastAPI

app = FastAPI(title="Symposium API")

@app.get("/api/v1/healthz/")
def health_check():
    return {"status": "ok"}