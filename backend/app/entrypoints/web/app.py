"""FastAPI application entry point."""
from fastapi import FastAPI

from app.auth.entrypoints import views as auth_views
from app.companies.entrypoints import views as companies_views
from app.ingestion.entrypoints import views as ingestion_views
from app.tracking.entrypoints import views as tracking_views
from app.users.entrypoints import views as users_views
from app.wagons.entrypoints import views as wagons_views

app = FastAPI(title="Wagon Monitor API", version="0.1.0")

app.include_router(auth_views.router)
app.include_router(companies_views.router)
app.include_router(users_views.router)
app.include_router(ingestion_views.router)
app.include_router(wagons_views.router)
app.include_router(tracking_views.router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
