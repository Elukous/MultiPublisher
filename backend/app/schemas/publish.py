"""Publish request/response schemas."""

from typing import Optional

from pydantic import BaseModel


class PublishRequest(BaseModel):
    content: str
    title: str
    platforms: list[str]
    metadata: dict = {}


class PlatformPublishResult(BaseModel):
    platform_id: str
    success: bool
    message: str
    simulated_url: Optional[str] = None
    content_to_copy: str
    timestamp: str
    platform_tip: Optional[str] = None


class PublishResponse(BaseModel):
    results: list[PlatformPublishResult]
    total_platforms: int
    successful: int
    failed: int
