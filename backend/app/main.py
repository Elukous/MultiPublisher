from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.platforms.registry import auto_register_platforms


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Ensure data directory exists
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    (settings.data_dir / "articles").mkdir(exist_ok=True)

    # Register all platform adapters
    auto_register_platforms()

    yield


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    return {"status": "ok", "app": settings.app_name}


# Import and include API router after app is created
from app.api.router import api_router  # noqa: E402

app.include_router(api_router, prefix="/api/v1")
