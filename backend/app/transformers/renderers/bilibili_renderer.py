"""Bilibili column content renderer.

Produces HTML compatible with Bilibili's article editor.
Supports standard HTML tags with moderate styling.
"""

from __future__ import annotations

from typing import Optional

from app.transformers.base_renderer import BaseRenderer
from app.transformers.intermediate import ContentAST
from app.utils.html_helpers import wrap_in_html_document


# Bilibili-compatible styles (less aggressive than WeChat)
BILI_STYLES = {
    'h2': 'font-size:22px; font-weight:bold; color:#212121; margin:28px 0 14px 0;',
    'h3': 'font-size:19px; font-weight:bold; color:#212121; margin:22px 0 10px 0;',
    'h4': 'font-size:17px; font-weight:bold; color:#333; margin:18px 0 8px 0;',
    'paragraph': 'font-size:15px; line-height:1.75; color:#333; margin:14px 0;',
    'code_inline': (
        'background:#f1f2f3; padding:2px 6px; border-radius:3px; '
        'font-size:90%; font-family:Menlo,Monaco,Consolas,monospace; color:#e96900;'
    ),
    'code_block': (
        'background:#1e1e1e; color:#d4d4d4; padding:16px; '
        'border-radius:6px; overflow-x:auto; font-size:14px; line-height:1.5; '
        'margin:14px 0;'
    ),
    'blockquote': (
        'border-left:4px solid #00a1d6; padding:12px 16px; '
        'color:#666; background:#f4f5f7; margin:14px 0;'
    ),
    'image': 'max-width:100%; display:block; margin:14px auto; border-radius:4px;',
    'hr': 'border:none; border-top:1px solid #e5e5e5; margin:20px 0;',
    'link': 'color:#00a1d6; text-decoration:none;',
    'table': 'width:100%; border-collapse:collapse; margin:14px 0;',
    'th': 'border:1px solid #e5e5e5; padding:10px; background:#f4f5f7; font-weight:bold;',
    'td': 'border:1px solid #e5e5e5; padding:10px;',
}


class BilibiliRenderer(BaseRenderer):
    """Renders ContentAST to Bilibili-compatible HTML."""

    def render(self, ast: ContentAST, metadata: Optional[dict] = None) -> str:
        """Render AST to Bilibili HTML."""
        metadata = metadata or {}
        parts: list[str] = []

        for token in ast.raw_tokens:
            html = self._render_token(token)
            if html:
                parts.append(html)

        return '\n'.join(parts)

    def _render_token(self, token: dict) -> str:
        """Render a single block-level token."""
        token_type = token.get('type', '')
        children = token.get('children', [])

        if token_type == 'heading':
            return self._render_heading(token)
        elif token_type == 'paragraph':
            return self._render_paragraph(token)
        elif token_type == 'block_code':
            return self._render_block_code(token)
        elif token_type == 'block_quote':
            return self._render_block_quote(token)
        elif token_type == 'list':
            return self._render_list(token)
        elif token_type == 'thematic_break':
            return f'<hr style="{BILI_STYLES["hr"]}" />'
        elif token_type == 'image':
            return self._render_image(token)
        elif token_type == 'table':
            return self._render_table(token)
        else:
            if children:
                inline = self._render_inline_html(children)
                return f'<p style="{BILI_STYLES["paragraph"]}">{inline}</p>'
            return ''

    def _render_heading(self, token: dict) -> str:
        level = token.get('attrs', {}).get('level', 2)
        tag = f'h{min(max(level, 2), 4)}'
        style = BILI_STYLES.get(f'h{min(max(level, 2), 4)}', BILI_STYLES['h2'])
        text = self._render_inline_html(token.get('children', []))
        return f'<{tag} style="{style}">{text}</{tag}>'

    def _render_paragraph(self, token: dict) -> str:
        text = self._render_inline_html(token.get('children', []))
        return f'<p style="{BILI_STYLES["paragraph"]}">{text}</p>'

    def _render_block_code(self, token: dict) -> str:
        lang = token.get('attrs', {}).get('info', '') or token.get('attrs', {}).get('language', '')
        code = self._escape_html(token.get('raw', ''))
        lang_class = f' class="language-{lang}"' if lang else ''
        return (
            f'<section style="{BILI_STYLES["code_block"]}">'
            f'<pre><code{lang_class}>{code}</code></pre></section>'
        )

    def _render_block_quote(self, token: dict) -> str:
        parts = []
        for child in token.get('children', []):
            if child.get('type') == 'paragraph':
                parts.append(self._render_inline_html(child.get('children', [])))
            else:
                parts.append(self._render_token(child))
        content = '<br>'.join(parts)
        return f'<blockquote style="{BILI_STYLES["blockquote"]}">{content}</blockquote>'

    def _render_list(self, token: dict) -> str:
        ordered = token.get('attrs', {}).get('ordered', False)
        tag = 'ol' if ordered else 'ul'
        items = []
        for child in token.get('children', []):
            if child.get('type') == 'list_item':
                item_text = self._render_list_item(child)
                items.append(f'<li>{item_text}</li>')
        return f'<{tag}>{"".join(items)}</{tag}>'

    def _render_list_item(self, token: dict) -> str:
        parts = []
        for child in token.get('children', []):
            if child.get('type') == 'paragraph':
                parts.append(self._render_inline_html(child.get('children', [])))
            elif child.get('type') == 'list':
                parts.append(self._render_list(child))
            else:
                parts.append(self._render_token(child))
        return ''.join(parts)

    def _render_image(self, token: dict) -> str:
        src = token.get('attrs', {}).get('url', '')
        alt = token.get('attrs', {}).get('alt', '')
        if not src:
            return ''
        return (
            f'<img src="{self._escape_html(src)}" '
            f'alt="{self._escape_html(alt)}" '
            f'style="{BILI_STYLES["image"]}" />'
        )

    def _render_table(self, token: dict) -> str:
        rows = token.get('children', [])
        if not rows:
            return ''

        html_parts = [f'<table style="{BILI_STYLES["table"]}">']
        for i, row in enumerate(rows):
            if row.get('type') != 'table_row':
                continue
            tag = 'th' if i == 0 else 'td'
            style = BILI_STYLES.get(tag, BILI_STYLES['td'])
            html_parts.append('<tr>')
            for cell in row.get('children', []):
                if cell.get('type') not in ('table_cell', 'table_head'):
                    continue
                content = self._render_inline_html(cell.get('children', []))
                html_parts.append(f'<{tag} style="{style}">{content}</{tag}>')
            html_parts.append('</tr>')

        html_parts.append('</table>')
        return ''.join(html_parts)

    def _render_inline_html(self, children: list[dict]) -> str:
        """Render inline tokens with Bilibili styling."""
        parts = []
        for child in children:
            child_type = child.get('type', '')
            if child_type == 'text':
                parts.append(self._escape_html(child.get('raw', '')))
            elif child_type == 'strong':
                inner = self._render_inline_html(child.get('children', []))
                parts.append(f'<strong>{inner}</strong>')
            elif child_type == 'emphasis':
                inner = self._render_inline_html(child.get('children', []))
                parts.append(f'<em>{inner}</em>')
            elif child_type == 'codespan':
                code = self._escape_html(child.get('raw', ''))
                parts.append(f'<code style="{BILI_STYLES["code_inline"]}">{code}</code>')
            elif child_type == 'link':
                inner = self._render_inline_html(child.get('children', []))
                href = child.get('attrs', {}).get('url', '#')
                # Auto-link BV numbers
                parts.append(
                    f'<a href="{self._escape_html(href)}" '
                    f'target="_blank" style="{BILI_STYLES["link"]}">{inner}</a>'
                )
            elif child_type == 'image':
                src = child.get('attrs', {}).get('url', '')
                alt = child.get('attrs', {}).get('alt', '')
                if src:
                    parts.append(
                        f'<img src="{self._escape_html(src)}" '
                        f'alt="{self._escape_html(alt)}" '
                        f'style="{BILI_STYLES["image"]}" />'
                    )
            elif child_type == 'softbreak':
                parts.append('\n')
            elif child_type == 'linebreak':
                parts.append('<br>')
            elif child_type == 'strikethrough':
                inner = self._render_inline_html(child.get('children', []))
                parts.append(f'<del>{inner}</del>')
            elif child.get('children'):
                parts.append(self._render_inline_html(child['children']))
            elif 'raw' in child:
                parts.append(self._escape_html(child['raw']))
        return ''.join(parts)
