"""Platform info schemas."""

from typing import Any

from pydantic import BaseModel


class PlatformInfo(BaseModel):
    id: str
    display_name: str
    icon: str
    description: str
    supports_preview: bool
    content_limits: dict[str, Any]
