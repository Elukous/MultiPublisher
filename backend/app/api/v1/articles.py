"""Articles CRUD API endpoints."""

from fastapi import APIRouter, HTTPException

from app.schemas.article import (
    ArticleCreate,
    ArticleListItem,
    ArticleResponse,
    ArticleUpdate,
)
from app.services.article_service import ArticleService

router = APIRouter()


def _get_service() -> ArticleService:
    return ArticleService()


@router.get('/articles', response_model=list[ArticleListItem])
async def list_articles():
    """List all saved articles."""
    service = _get_service()
    return service.list_all()


@router.post('/articles', response_model=ArticleResponse, status_code=201)
async def create_article(request: ArticleCreate):
    """Create a new article."""
    service = _get_service()
    return service.create(
        title=request.title,
        content=request.content,
        tags=request.tags,
        cover_image=request.cover_image,
    )


@router.get('/articles/{article_id}', response_model=ArticleResponse)
async def get_article(article_id: str):
    """Get a single article by ID."""
    service = _get_service()
    article = service.get(article_id)
    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    return article


@router.put('/articles/{article_id}', response_model=ArticleResponse)
async def update_article(article_id: str, request: ArticleUpdate):
    """Update an existing article."""
    service = _get_service()
    article = service.update(
        article_id,
        title=request.title,
        content=request.content,
        tags=request.tags,
        cover_image=request.cover_image,
    )
    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    return article


@router.delete('/articles/{article_id}')
async def delete_article(article_id: str):
    """Delete an article."""
    service = _get_service()
    if not service.delete(article_id):
        raise HTTPException(status_code=404, detail="Article not found")
    return {'message': 'Article deleted'}
