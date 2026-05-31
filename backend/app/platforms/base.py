from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Optional

from app.transformers.intermediate import ContentAST


class PlatformAdapter(ABC):
    """Abstract base class for all platform adapters.

    To add a new platform:
    1. Subclass this and implement all abstract methods.
    2. Call registry.register(YourPlatform()) at module level.
    3. Import your module in registry.py's auto_register_platforms().
    """

    @property
    @abstractmethod
    def platform_id(self) -> str:
        """Unique identifier, e.g. 'wechat', 'zhihu'."""
        ...

    @property
    @abstractmethod
    def display_name(self) -> str:
        """Human-readable name, e.g. '微信公众号'."""
        ...

    @property
    @abstractmethod
    def icon(self) -> str:
        """Icon identifier or emoji for frontend display."""
        ...

    @property
    def description(self) -> str:
        """Short description of the platform."""
        return ''

    @property
    def content_limits(self) -> dict[str, Any]:
        """Platform content constraints for frontend guidance."""
        return {}

    @abstractmethod
    def transform(self, ast: ContentAST, metadata: Optional[dict] = None) -> str:
        """Convert intermediate AST to platform-specific output format.

        Args:
            ast: Parsed content tree from the markdown parser.
            metadata: Article metadata (title, tags, cover_image, etc.)

        Returns:
            Platform-formatted content string (HTML, Markdown, or plain text).
        """
        ...

    @abstractmethod
    def generate_preview_html(self, transformed_content: str) -> str:
        """Wrap transformed content in a standalone HTML document for iframe preview.

        Returns:
            Complete HTML document string suitable for rendering in an iframe.
        """
        ...

    @abstractmethod
    def validate(self, transformed_content: str, metadata: Optional[dict] = None) -> list[dict]:
        """Check content against platform constraints.

        Returns:
            List of validation warnings/errors, each a dict:
            {'level': 'warning'|'error', 'message': str, 'field': str}
        """
        ...

    @abstractmethod
    def simulate_publish(self, transformed_content: str, metadata: Optional[dict] = None) -> dict:
        """Simulate publishing to this platform (V1: no real API calls).

        Returns:
            Dict with 'success', 'message', 'simulated_url', 'timestamp'.
        """
        ...

    def get_platform_info(self) -> dict[str, Any]:
        """Return platform metadata for the frontend."""
        return {
            'id': self.platform_id,
            'display_name': self.display_name,
            'icon': self.icon,
            'description': self.description,
            'supports_preview': True,
            'content_limits': self.content_limits,
        }

    def _make_simulated_result(
        self,
        success: bool = True,
        message: str = '',
        extra: Optional[dict] = None,
    ) -> dict:
        """Helper to build a simulated publish result dict."""
        result = {
            'success': success,
            'message': message,
            'simulated_url': f'https://example.com/{self.platform_id}/article/simulated',
            'timestamp': datetime.now(timezone.utc).isoformat(),
        }
        if extra:
            result.update(extra)
        return result
