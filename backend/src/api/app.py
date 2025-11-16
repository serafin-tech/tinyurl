"""FastAPI application entrypoint for TinyURL Backend MVP."""

from fastapi import FastAPI

app = FastAPI(title="TinyURL Backend MVP", version="0.1.0")

@app.get("/api/health")
async def health() -> dict[str, str]:
    """Simple health check endpoint."""
    return {"status": "ok"}
