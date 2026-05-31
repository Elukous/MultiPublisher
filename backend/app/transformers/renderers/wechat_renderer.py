"""WeChat Official Account content renderer.

Produces fully inline-styled HTML suitable for WeChat's article editor.
WeChat strips <style> tags, so all CSS must be inlined.
"""

from __future__ import annotations

from typing import Optional

from app.transformers.base_renderer import BaseRenderer
from app.transformers.intermediate import ContentAST
from app.utils.html_helpers import wrap_in_html_document


# WeChat-specific inline styles
WECHAT_STYLES = {
    'wrapper': (
        'max-width:900px; margin:0 auto; '
        'font-family:"PingFang SC","Microsoft YaHei",sans-serif; '
        'color:#333; padding:16px;'
    ),
    'h2': (
        'font-size:22px; font-weight:bold; color:#1a1a1a; '
        'border-bottom:2px solid #3eaf7c; padding-bottom:8px; '
        'margin:28px 0 16px 0;'
    ),
    'h3': (
        'font-size:19px; font-weight:bold; color:#1a1a1a; '
        'margin:24px 0 12px 0;'
    ),
    'h4': (
        'font-size:17px; font-weight:bold; color:#333; '
        'margin:20px 0 10px 0;'
    ),
    'paragraph': (
        'font-size:16px; line-height:1.8; color:#333; '
        'margin:16px 0; letter-spacing:1px; '
        'text-align:justify;'
    ),
    'strong': 'color:#1a1a1a; font-weight:bold;',
    'emphasis': 'font-style:italic; color:#555;',
    'code_inline': (
        'background:#f0f0f0; padding:2px 6px; border-radius:3px; '
        'font-size:90%; font-family:"SFMono-Regular",Consolas,"Liberation Mono",Menlo,monospace; '
        'color:#e96900;'
    ),
    'code_block': (
        'background:#282c34; color:#abb2bf; padding:16px; '
        'border-radius:5px; font-family:"SFMono-Regular",Consolas,"Liberation Mono",Menlo,monospace; '
        'overflow-x:auto; font-size:14px; line-height:1.6; '
        'margin:16px 0;'
    ),
    'blockquote': (
        'border-left:4px solid #3eaf7c; padding:12px 16px; '
        'color:#666; background:#f8f8f8; margin:16px 0; '
        'font-size:15px; line-height:1.7;'
    ),
    'image': (
        'max-width:100%; display:block; margin:16px auto; '
        'border-radius:4px;'
    ),
    'hr': 'border:none; border-top:1px solid #ddd; margin:24px 0;',
    'ul': 'padding-left:24px; margin:12px 0; line-height:1.8;',
    'ol': 'padding-left:24px; margin:12px 0; line-height:1.8;',
    'li': 'font-size:16px; line-height:1.8; margin:6px 0; color:#333;',
    'link': 'color:#3eaf7c; text-decoration:none; border-bottom:1px solid #3eaf7c;',
    'table_wrapper': 'overflow-x:auto; margin:16px 0;',
    'table': 'width:100%; border-collapse:collapse; font-size:15px;',
    'th': (
        'border:1px solid #ddd; padding:10px 14px; '
        'background:#f8f8f8; font-weight:bold; text-align:left;'
    ),
    'td': 'border:1px solid #ddd; padding:10px 14px;',
}


class WeChatRenderer(BaseRenderer):
    """Renders ContentAST to WeChat-compatible inline-styled HTML."""

    def render(self, ast: ContentAST, metadata: Optional[dict] = None) -> str:
        """Render AST to WeChat HTML with all styles inlined."""
        metadata = metadata or {}
        parts: list[str] = []

        for token in ast.raw_tokens:
            html = self._render_token(token)
            if html:
                parts.append(html)

        body = '\n'.join(parts)

        # Wrap in WeChat content container
        return f'<section style="{WECHAT_STYLES["wrapper"]}">\n{body}\n</section>'

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
            return f'<hr style="{WECHAT_STYLES["hr"]}" />'
        elif token_type == 'image':
            return self._render_image(token)
        elif token_type == 'table':
            return self._render_table(token)
        else:
            # Unknown block type: render children as inline
            if children:
                inline = self._render_inline_styled(children)
                return f'<p style="{WECHAT_STYLES["paragraph"]}">{inline}</p>'
            return ''

    def _render_heading(self, token: dict) -> str:
        level = token.get('attrs', {}).get('level', 2)
        # WeChat: skip h1 (use h2-h4), clamp to h4 max
        tag = f'h{min(max(level, 2), 4)}'
        style_key = f'h{min(max(level, 2), 4)}'
        style = WECHAT_STYLES.get(style_key, WECHAT_STYLES['h2'])
        text = self._render_inline_styled(token.get('children', []))
        return f'<{tag} style="{style}">{text}</{tag}>'

    def _render_paragraph(self, token: dict) -> str:
        text = self._render_inline_styled(token.get('children', []))
        return f'<p style="{WECHAT_STYLES["paragraph"]}">{text}</p>'

    def _render_block_code(self, token: dict) -> str:
        code = token.get('raw', '')
        code = self._escape_html(code)
        return (
            f'<section style="{WECHAT_STYLES["code_block"]}">'
            f'<pre>{code}</pre></section>'
        )

    def _render_block_quote(self, token: dict) -> str:
        parts = []
        for child in token.get('children', []):
            if child.get('type') == 'paragraph':
                parts.append(self._render_inline_styled(child.get('children', [])))
            else:
                parts.append(self._render_token(child))
        content = '<br>'.join(parts)
        return f'<blockquote style="{WECHAT_STYLES["blockquote"]}">{content}</blockquote>'

    def _render_list(self, token: dict) -> str:
        ordered = token.get('attrs', {}).get('ordered', False)
        tag = 'ol' if ordered else 'ul'
        style = WECHAT_STYLES[tag]
        items = []
        for child in token.get('children', []):
            if child.get('type') == 'list_item':
                item_text = self._render_list_item(child)
                items.append(f'<li style="{WECHAT_STYLES["li"]}">{item_text}</li>')
        return f'<{tag} style="{style}">{"".join(items)}</{tag}>'

    def _render_list_item(self, token: dict) -> str:
        parts = []
        for child in token.get('children', []):
            if child.get('type') == 'paragraph':
                parts.append(self._render_inline_styled(child.get('children', [])))
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
            f'style="{WECHAT_STYLES["image"]}" />'
        )

    def _render_table(self, token: dict) -> str:
        rows = token.get('children', [])
        if not rows:
            return ''

        html_parts = [f'<div style="{WECHAT_STYLES["table_wrapper"]}">']
        html_parts.append(f'<table style="{WECHAT_STYLES["table"]}">')

        for i, row in enumerate(rows):
            if row.get('type') != 'table_row':
                continue
            tag = 'th' if i == 0 else 'td'
            style = WECHAT_STYLES.get(tag, WECHAT_STYLES['td'])
            cells = row.get('children', [])
            html_parts.append('<tr>')
            for cell in cells:
                if cell.get('type') not in ('table_cell', 'table_head'):
                    continue
                content = self._render_inline_styled(cell.get('children', []))
                html_parts.append(f'<{tag} style="{style}">{content}</{tag}>')
            html_parts.append('</tr>')

        html_parts.append('</table></div>')
        return ''.join(html_parts)

    def _render_inline_styled(self, children: list[dict]) -> str:
        """Render inline tokens with WeChat-specific styling."""
        parts = []
        for child in children:
            child_type = child.get('type', '')
            if child_type == 'text':
                parts.append(self._escape_html(child.get('raw', '')))
            elif child_type == 'strong':
                inner = self._render_inline_styled(child.get('children', []))
                parts.append(f'<strong style="{WECHAT_STYLES["strong"]}">{inner}</strong>')
            elif child_type == 'emphasis':
                inner = self._render_inline_styled(child.get('children', []))
                parts.append(f'<em style="{WECHAT_STYLES["emphasis"]}">{inner}</em>')
            elif child_type == 'codespan':
                code = self._escape_html(child.get('raw', ''))
                parts.append(f'<code style="{WECHAT_STYLES["code_inline"]}">{code}</code>')
            elif child_type == 'link':
                inner = self._render_inline_styled(child.get('children', []))
                href = child.get('attrs', {}).get('url', '#')
                parts.append(
                    f'<a href="{self._escape_html(href)}" '
                    f'style="{WECHAT_STYLES["link"]}">{inner}</a>'
                )
            elif child_type == 'image':
                src = child.get('attrs', {}).get('url', '')
                alt = child.get('attrs', {}).get('alt', '')
                if src:
                    parts.append(
                        f'<img src="{self._escape_html(src)}" '
                        f'alt="{self._escape_html(alt)}" '
                        f'style="{WECHAT_STYLES["image"]}" />'
                    )
            elif child_type == 'softbreak':
                parts.append('\n')
            elif child_type == 'linebreak':
                parts.append('<br>')
            elif child_type == 'strikethrough':
                inner = self._render_inline_styled(child.get('children', []))
                parts.append(f'<del>{inner}</del>')
            elif child.get('children'):
                parts.append(self._render_inline_styled(child['children']))
            elif 'raw' in child:
                parts.append(self._escape_html(child['raw']))
        return ''.join(parts)
