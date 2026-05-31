"""Transform service: orchestrates Markdown -> AST -> platform format pipeline."""

from __future__ import annotations

from typing import Optional

from app.platforms.registry import PlatformRegistry, registry
from app.transformers.intermediate import ContentAST
from app.transformers.parser import parse_markdown


class TransformService:
    """Orchestrates the content transformation pipeline."""

    def __init__(self, platform_registry: PlatformRegistry | None = None) -> None:
        self._registry = platform_registry or registry

    def parse(self, content: str, title: Optional[str] = None) -> ContentAST:
        """Parse markdown content into ContentAST."""
        tokens = parse_markdown(content)
        return ContentAST.from_tokens(tokens, title=title)

    def transform_for_platform(
        self, content: str, platform_id: str, metadata: Optional[dict] = None
    ) -> tuple[str, ContentAST]:
        """Transform content for a specific platform.

        Returns:
            Tuple of (transformed_content, ast).
        """
        ast = self.parse(content, title=metadata.get('title') if metadata else None)
        adapter = self._registry.get(platform_id)
        transformed = adapter.transform(ast, metadata)
        return transformed, ast

    def generate_preview(
        self, content: str, platform_id: str, metadata: Optional[dict] = None
    ) -> dict:
        """Generate a full preview for a platform.

        Returns dict with: html, raw_content, warnings, metadata.
        """
        transformed, ast = self.transform_for_platform(content, platform_id, metadata)
        adapter = self._registry.get(platform_id)
        preview_html = adapter.generate_preview_html(transformed)
        warnings = adapter.validate(transformed, metadata)

        return {
            'platform_id': platform_id,
            'html': preview_html,
            'raw_content': transformed,
            'warnings': warnings,
            'metadata': {
                'word_count': ast.word_count,
                'image_count': len(ast.images),
                'has_code_blocks': ast.has_code_blocks,
                'has_tables': ast.has_tables,
            },
        }
