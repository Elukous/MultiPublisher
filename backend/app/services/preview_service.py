"""Preview service: generates previews for one or more platforms."""

from __future__ import annotations

from typing import Optional

from app.services.transform_service import TransformService


class PreviewService:
    """Generates content previews for platforms."""

    def __init__(self, transform_service: TransformService | None = None) -> None:
        self._transform = transform_service or TransformService()

    def generate_single(
        self, content: str, platform_id: str, metadata: Optional[dict] = None
    ) -> dict:
        """Generate preview for a single platform."""
        return self._transform.generate_preview(content, platform_id, metadata)

    def generate_batch(
        self, content: str, platform_ids: list[str], metadata: Optional[dict] = None
    ) -> list[dict]:
        """Generate previews for multiple platforms."""
        results = []
        for pid in platform_ids:
            try:
                preview = self.generate_single(content, pid, metadata)
                results.append(preview)
            except Exception as e:
                results.append({
                    'platform_id': pid,
                    'html': f'<p style="color:red;">预览生成失败: {e}</p>',
                    'raw_content': '',
                    'warnings': [{'level': 'error', 'message': str(e), 'field': 'content'}],
                    'metadata': {},
                })
        return results
