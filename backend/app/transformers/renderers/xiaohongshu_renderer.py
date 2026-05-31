"""Xiaohongshu (Little Red Book) content renderer.

Produces short-form content with emoji suggestions, tag extraction,
and aggressive text condensation for XHS's 1000-character limit.
"""

from __future__ import annotations

import json
from typing import Optional

from app.transformers.base_renderer import BaseRenderer
from app.transformers.intermediate import ContentAST
from app.utils.text_processing import (
    count_chars,
    extract_tags,
    suggest_emojis,
    truncate_text,
)


XHS_TITLE_LIMIT = 20
XHS_BODY_LIMIT = 1000


class XiaohongshuRenderer(BaseRenderer):
    """Renders ContentAST to Xiaohongshu short-text format with suggestions."""

    def render(self, ast: ContentAST, metadata: Optional[dict] = None) -> str:
        """Render AST to XHS-compatible short text with emoji suggestions.

        Returns a JSON string containing the adapted content and metadata.
        """
        metadata = metadata or {}

        # Extract title
        title = metadata.get('title') or ast.title or ''
        title = self._adapt_title(title)

        # Condense body text
        full_text = ast.get_text_content()
        body = self._condense_body(full_text)

        # Generate suggestions
        emojis = suggest_emojis(full_text)
        tags = extract_tags(full_text)

        # Build structured output
        result = {
            'title': title,
            'title_suggestions': self._generate_title_suggestions(
                metadata.get('title') or ast.title or '', emojis
            ),
            'body': body,
            'body_with_emoji': self._add_emoji_to_body(body, emojis),
            'suggested_tags': tags,
            'emoji_suggestions': emojis,
            'image_count': len(ast.images),
            'image_warnings': self._check_images(ast.images),
            'char_count': count_chars(body),
            'char_limit': XHS_BODY_LIMIT,
            'warnings': [],
        }

        # Add warnings
        if ast.has_code_blocks:
            result['warnings'].append('小红书不支持代码块，已转换为文字描述')
        if ast.has_tables:
            result['warnings'].append('小红书不支持表格，已转换为文字列表')
        if count_chars(body) > XHS_BODY_LIMIT:
            result['warnings'].append(f'正文超过{XHS_BODY_LIMIT}字限制，已截断')

        return json.dumps(result, ensure_ascii=False, indent=2)

    def _adapt_title(self, title: str) -> str:
        """Adapt title to XHS's 20-character limit."""
        if not title:
            return ''
        if len(title) <= XHS_TITLE_LIMIT:
            return title
        # Try to keep the most meaningful part
        return truncate_text(title, XHS_TITLE_LIMIT)

    def _condense_body(self, full_text: str) -> str:
        """Condense full article text to fit XHS character limit."""
        if count_chars(full_text) <= XHS_BODY_LIMIT:
            return full_text.strip()

        # Strategy: truncate with sentence boundary awareness
        return truncate_text(full_text, XHS_BODY_LIMIT)

    def _generate_title_suggestions(self, original_title: str, emojis: list[str]) -> list[str]:
        """Generate alternative title suggestions with emojis."""
        suggestions = []
        if not original_title:
            return suggestions

        base = original_title[:XHS_TITLE_LIMIT]

        # Suggestion 1: with leading emoji
        if emojis:
            emoji_prefix = emojis[0]
            adapted = f'{emoji_prefix}{base}'
            if len(adapted) <= XHS_TITLE_LIMIT + 2:  # Allow slight overshoot for emoji
                suggestions.append(adapted)

        # Suggestion 2: with suffix tag
        if len(base) < XHS_TITLE_LIMIT - 5:
            suggestions.append(f'{base}|必看')

        # Suggestion 3: original (truncated if needed)
        suggestions.append(base)

        return suggestions[:3]

    def _add_emoji_to_body(self, body: str, emojis: list[str]) -> str:
        """Add emoji decorations to body text."""
        if not body or not emojis:
            return body

        lines = body.split('\n')
        result_lines = []

        for i, line in enumerate(lines):
            if not line.strip():
                result_lines.append(line)
                continue

            if i == 0:
                # Start emoji
                line = f'{emojis[0]} {line}'
            elif line.startswith('-') or line.startswith('•'):
                # List item emoji
                emoji = emojis[1] if len(emojis) > 1 else '👉'
                line = f'{emoji} {line}'
            result_lines.append(line)

        return '\n'.join(result_lines)

    def _check_images(self, images: list[str]) -> list[str]:
        """Check image requirements and return warnings."""
        warnings = []
        if len(images) < 3:
            warnings.append(f'至少需要3张图片，当前仅有{len(images)}张')
        if len(images) > 18:
            warnings.append(f'最多支持18张图片，当前有{len(images)}张')
        warnings.append('建议使用 3:4 竖版配图')
        return warnings
