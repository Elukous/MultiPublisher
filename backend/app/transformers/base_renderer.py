from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from app.transformers.intermediate import ContentAST


class BaseRenderer(ABC):
    """Base class for all platform content renderers.

    Subclasses implement render() to produce platform-specific output
    from the ContentAST intermediate representation.
    """

    @abstractmethod
    def render(self, ast: ContentAST, metadata: Optional[dict] = None) -> str:
        """Render the AST into platform-specific output.

        Args:
            ast: Parsed content tree.
            metadata: Optional metadata dict (title, tags, cover_image, etc.)

        Returns:
            Platform-formatted content string (HTML, Markdown, or plain text).
        """
        ...

    # ---- Common helpers for all renderers ----

    def _render_inline(self, children: list[dict]) -> str:
        """Render inline tokens to plain text. Subclasses override for styled output."""
        parts = []
        for child in children:
            child_type = child.get('type', '')
            if child_type == 'text':
                parts.append(child.get('raw', ''))
            elif child_type == 'strong':
                inner = self._render_inline(child.get('children', []))
                parts.append(inner)
            elif child_type == 'emphasis':
                inner = self._render_inline(child.get('children', []))
                parts.append(inner)
            elif child_type == 'codespan':
                parts.append(child.get('raw', ''))
            elif child_type == 'link':
                inner = self._render_inline(child.get('children', []))
                parts.append(inner)
            elif child_type == 'image':
                alt = child.get('attrs', {}).get('alt', '')
                parts.append(alt)
            elif child_type == 'softbreak':
                parts.append('\n')
            elif child_type == 'linebreak':
                parts.append('\n')
            elif child.get('children'):
                parts.append(self._render_inline(child['children']))
            elif 'raw' in child:
                parts.append(child['raw'])
        return ''.join(parts)

    def _escape_html(self, text: str) -> str:
        """Escape HTML special characters."""
        return (
            text.replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
            .replace('"', '&quot;')
            .replace("'", '&#39;')
        )

    def _get_attr(self, token: dict, key: str, default: str = '') -> str:
        """Safely get an attribute from a token's attrs dict."""
        return token.get('attrs', {}).get(key, default)
