"""Preview request/response schemas."""

from typing import Optional

from pydantic import BaseModel


class PreviewRequest(BaseModel):
    content: str
    title: Optional[str] = None
    metadata: dict = {}


class PlatformWarning(BaseModel):
    level: str  # "warning" or "error"
    message: str
    field: Optional[str] = None


class PreviewResponse(BaseModel):
    platform_id: str
    html: str
    raw_content: str
    warnings: list[PlatformWarning]
    metadata: dict = {}


class BatchPreviewRequest(BaseModel):
    content: str
    title: Optional[str] = None
    platforms: list[str] = []
    metadata: dict = {}


class BatchPreviewResponse(BaseModel):
    previews: list[PreviewResponse]
