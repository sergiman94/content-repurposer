"""FastAPI application - placeholder for Phase 2."""

from fastapi import FastAPI

app = FastAPI(title="Content Repurposer", version="0.1.0")


@app.get("/api/health")
async def health():
    return {"status": "ok"}
