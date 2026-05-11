"""FastAPI application entry point."""
from fastapi import FastAPI

from app.auth.entrypoints import views as auth_views

app = FastAPI(title="Wagon Monitor API", version="0.1.0")

app.include_router(auth_views.router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
