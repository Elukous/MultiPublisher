"""Publish service: orchestrates simulated publishing to platforms."""

from __future__ import annotations

from typing import Optional

from app.platforms.registry import PlatformRegistry, registry
from app.services.transform_service import TransformService


class PublishService:
    """Handles simulated publishing to multiple platforms."""

    def __init__(
        self,
        transform_service: TransformService | None = None,
        platform_registry: PlatformRegistry | None = None,
    ) -> None:
        self._transform = transform_service or TransformService()
        self._registry = platform_registry or registry

    def publish(
        self, content: str, title: str, platform_ids: list[str], metadata: Optional[dict] = None
    ) -> dict:
        """Simulate publishing to all selected platforms.

        Returns dict with: results, total_platforms, successful, failed.
        """
        metadata = metadata or {}
        metadata['title'] = title

        results = []
        for pid in platform_ids:
            try:
                adapter = self._registry.get(pid)
                transformed, _ = self._transform.transform_for_platform(
                    content, pid, metadata
                )
                result = adapter.simulate_publish(transformed, metadata)
                results.append({
                    'platform_id': pid,
                    'success': result.get('success', True),
                    'message': result.get('message', ''),
                    'simulated_url': result.get('simulated_url'),
                    'content_to_copy': result.get('content_to_copy', transformed),
                    'timestamp': result.get('timestamp', ''),
                    'platform_tip': result.get('platform_tip'),
                })
            except Exception as e:
                results.append({
                    'platform_id': pid,
                    'success': False,
                    'message': f'发布失败: {e}',
                    'simulated_url': None,
                    'content_to_copy': '',
                    'timestamp': '',
                    'platform_tip': None,
                })

        return {
            'results': results,
            'total_platforms': len(platform_ids),
            'successful': sum(1 for r in results if r['success']),
            'failed': sum(1 for r in results if not r['success']),
        }
