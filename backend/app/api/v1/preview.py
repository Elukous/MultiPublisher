"""Preview API endpoints."""

from fastapi import APIRouter, HTTPException

from app.schemas.preview import (
    BatchPreviewRequest,
    BatchPreviewResponse,
    PreviewRequest,
    PreviewResponse,
    PlatformWarning,
)
from app.services.preview_service import PreviewService
from app.services.transform_service import TransformService

router = APIRouter()


def _get_preview_service() -> PreviewService:
    return PreviewService(TransformService())


# IMPORTANT: /batch must be defined BEFORE /{platform_id} to avoid path collision
@router.post('/preview/batch', response_model=BatchPreviewResponse)
async def preview_batch(request: BatchPreviewRequest):
    """Generate previews for multiple platforms at once."""
    from app.platforms.registry import registry

    # Default to all platforms if none specified
    platform_ids = request.platforms or registry.list_ids()

    # Validate platform IDs
    for pid in platform_ids:
        if pid not in registry:
            raise HTTPException(status_code=404, detail=f"Platform '{pid}' not found")

    service = _get_preview_service()
    metadata = {**request.metadata}
    if request.title:
        metadata['title'] = request.title

    results = service.generate_batch(request.content, platform_ids, metadata)
    previews = [
        PreviewResponse(
            platform_id=r['platform_id'],
            html=r['html'],
            raw_content=r['raw_content'],
            warnings=[PlatformWarning(**w) for w in r['warnings']],
            metadata=r.get('metadata', {}),
        )
        for r in results
    ]
    return BatchPreviewResponse(previews=previews)


@router.post('/preview/{platform_id}', response_model=PreviewResponse)
async def preview_single(platform_id: str, request: PreviewRequest):
    """Generate preview for a single platform."""
    from app.platforms.registry import registry

    if platform_id not in registry:
        raise HTTPException(status_code=404, detail=f"Platform '{platform_id}' not found")

    service = _get_preview_service()
    metadata = {**request.metadata}
    if request.title:
        metadata['title'] = request.title

    result = service.generate_single(request.content, platform_id, metadata)
    return PreviewResponse(
        platform_id=result['platform_id'],
        html=result['html'],
        raw_content=result['raw_content'],
        warnings=[PlatformWarning(**w) for w in result['warnings']],
        metadata=result.get('metadata', {}),
    )
