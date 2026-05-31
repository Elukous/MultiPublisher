"""Platforms API endpoints — list, manage custom, and hot-reload."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.dependencies import get_registry
from app.platforms.registry import (
    CUSTOM_PLATFORMS_FILE,
    registry,
    reload_plugins,
    save_custom_platforms,
)
from app.schemas.platform import PlatformInfo

router = APIRouter()


@router.get('/platforms', response_model=list[PlatformInfo])
async def list_platforms():
    """List all registered platforms (built-in + plugin + custom)."""
    return [adapter.get_platform_info() for adapter in registry.list_all()]


# ---- Custom platform management ----

class CustomPlatformDef(BaseModel):
    id: str
    name: str
    icon: str = '🔌'
    description: str = ''
    format: str = 'html'  # html, markdown, plain_text, json
    style_preset: str = 'desktop'  # mobile, desktop, minimal
    header_template: str = ''
    footer_template: str = ''
    preprocessor: dict = {}
    content_limits: dict = {}


@router.get('/platforms/custom', response_model=list[CustomPlatformDef])
async def list_custom_platforms():
    """List user-defined custom platforms from config file."""
    if not CUSTOM_PLATFORMS_FILE.exists():
        return []
    import json
    try:
        data = json.loads(CUSTOM_PLATFORMS_FILE.read_text(encoding='utf-8'))
        return [CustomPlatformDef(**d) for d in data]
    except Exception:
        return []


@router.post('/platforms/custom', response_model=list[PlatformInfo])
async def save_custom_platform(platform: CustomPlatformDef):
    """Create or update a custom platform config and hot-reload."""
    platform_id = platform.id
    existing = await list_custom_platforms()

    # Validate ID format
    if not platform_id.replace('_', '').replace('-', '').isalnum():
        raise HTTPException(status_code=400, detail='平台 ID 只能包含字母、数字、下划线和连字符')

    # Update or append
    updated_list = []
    found = False
    for p in existing:
        if p.id == platform_id:
            updated_list.append(platform.model_dump())
            found = True
        else:
            updated_list.append(p.model_dump())

    if not found:
        updated_list.append(platform.model_dump())

    all_infos = save_custom_platforms(updated_list)
    return [info for info in all_infos if not info['id'].startswith('custom_') or info['id'] == f'custom_{platform_id}']


@router.delete('/platforms/custom/{platform_id}', response_model=list[PlatformInfo])
async def delete_custom_platform(platform_id: str):
    """Delete a custom platform config and hot-reload."""
    existing = await list_custom_platforms()
    updated = [p.model_dump() for p in existing if p.id != platform_id]

    if len(updated) == len(existing):
        raise HTTPException(status_code=404, detail='自定义平台未找到')

    all_infos = save_custom_platforms(updated)
    return all_infos


# ---- Plugin hot-reload ----

@router.post('/platforms/reload', response_model=list[PlatformInfo])
async def reload_platforms():
    """Hot-reload all plugins and custom platforms from disk."""
    infos = reload_plugins()
    return infos
