from fastapi import FastAPI

from app.config import get_settings
from app.database import initialize_database
from app.routes.monitors import router as monitors_router


settings = get_settings()
app = FastAPI(title=settings.app_name)
app.include_router(monitors_router)


@app.on_event("startup")
def startup() -> None:
    initialize_database()


@app.get("/health")
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "service": settings.app_name,
        "environment": settings.environment,
    }
