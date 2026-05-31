"""Publish API endpoint (simulated)."""

from fastapi import APIRouter, HTTPException

from app.schemas.publish import (
    PlatformPublishResult,
    PublishRequest,
    PublishResponse,
)
from app.services.publish_service import PublishService
from app.services.transform_service import TransformService

router = APIRouter()


@router.post('/publish', response_model=PublishResponse)
async def simulate_publish(request: PublishRequest):
    """Simulate publishing to selected platforms."""
    from app.platforms.registry import registry

    if not request.platforms:
        raise HTTPException(status_code=400, detail="No platforms specified")

    for pid in request.platforms:
        if pid not in registry:
            raise HTTPException(status_code=404, detail=f"Platform '{pid}' not found")

    service = PublishService(TransformService())
    result = service.publish(
        content=request.content,
        title=request.title,
        platform_ids=request.platforms,
        metadata=request.metadata,
    )

    return PublishResponse(
        results=[PlatformPublishResult(**r) for r in result['results']],
        total_platforms=result['total_platforms'],
        successful=result['successful'],
        failed=result['failed'],
    )
