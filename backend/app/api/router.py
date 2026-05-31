from fastapi import APIRouter

from app.api.v1.articles import router as articles_router
from app.api.v1.platforms import router as platforms_router
from app.api.v1.preview import router as preview_router
from app.api.v1.publish import router as publish_router

api_router = APIRouter()

api_router.include_router(platforms_router, tags=["platforms"])
api_router.include_router(preview_router, tags=["preview"])
api_router.include_router(publish_router, tags=["publish"])
api_router.include_router(articles_router, tags=["articles"])
