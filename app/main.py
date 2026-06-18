from fastapi import FastAPI

from app.config import get_settings
from app.database import initialize_database
from app.routes.monitors import router as monitors_router
from app.scheduler import create_scheduler


settings = get_settings()
app = FastAPI(title=settings.app_name)
app.include_router(monitors_router)
scheduler = create_scheduler()


@app.on_event("startup")
def startup() -> None:
    initialize_database()
    if not scheduler.running:
        scheduler.start()


@app.on_event("shutdown")
def shutdown() -> None:
    if scheduler.running:
        scheduler.shutdown()


@app.get("/health")
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "service": settings.app_name,
        "environment": settings.environment,
    }
