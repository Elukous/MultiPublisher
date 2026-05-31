"""Zhihu content renderer.

Produces clean Markdown following Zhihu's formatting conventions.
Zhihu's editor natively supports Markdown input.
"""

from __future__ import annotations

from typing import Optional

from app.transformers.base_renderer import BaseRenderer
from app.transformers.intermediate import ContentAST
from app.utils.text_processing import add_space_between_cn_en


class ZhihuRenderer(BaseRenderer):
    """Renders ContentAST to Zhihu-compatible clean Markdown."""

    def render(self, ast: ContentAST, metadata: Optional[dict] = None) -> str:
        """Render AST to clean Markdown for Zhihu."""
        metadata = metadata or {}
        parts: list[str] = []

        for token in ast.raw_tokens:
            md = self._render_token(token)
            if md:
                parts.append(md)

        result = '\n\n'.join(parts)

        # Apply Zhihu formatting norms: add spaces between Chinese and English
        result = add_space_between_cn_en(result)

        return result

    def _render_token(self, token: dict) -> str:
        """Render a single block-level token to Markdown."""
        token_type = token.get('type', '')
        children = token.get('children', [])

        if token_type == 'heading':
            return self._render_heading(token)
        elif token_type == 'paragraph':
            return self._render_inline_md(children)
        elif token_type == 'block_code':
            return self._render_block_code(token)
        elif token_type == 'block_quote':
            return self._render_block_quote(token)
        elif token_type == 'list':
            return self._render_list(token)
        elif token_type == 'thematic_break':
            return '---'
        elif token_type == 'image':
            return self._render_image_md(token)
        elif token_type == 'table':
            return self._render_table_md(token)
        else:
            if children:
                return self._render_inline_md(children)
            return ''

    def _render_heading(self, token: dict) -> str:
        level = token.get('attrs', {}).get('level', 2)
        # Zhihu uses article title as H1, so start from ##
        level = max(level + 1, 2)
        level = min(level, 5)  # Zhihu supports up to h5
        prefix = '#' * level
        text = self._render_inline_md(token.get('children', []))
        return f'{prefix} {text}'

    def _render_block_code(self, token: dict) -> str:
        lang = token.get('attrs', {}).get('info', '') or token.get('attrs', {}).get('language', '')
        code = token.get('raw', '')
        return f'```{lang}\n{code}\n```'

    def _render_block_quote(self, token: dict) -> str:
        parts = []
        for child in token.get('children', []):
            child_type = child.get('type', '')
            if child_type == 'paragraph':
                parts.append(self._render_inline_md(child.get('children', [])))
            else:
                rendered = self._render_token(child)
                if rendered:
                    parts.append(rendered)
        content = '\n>\n'.join(parts)
        lines = content.split('\n')
        return '\n'.join(f'> {line}' for line in lines)

    def _render_list(self, token: dict) -> str:
        ordered = token.get('attrs', {}).get('ordered', False)
        items = []
        for idx, child in enumerate(token.get('children', []), 1):
            if child.get('type') == 'list_item':
                item_text = self._render_list_item_md(child)
                if ordered:
                    items.append(f'{idx}. {item_text}')
                else:
                    items.append(f'- {item_text}')
        return '\n'.join(items)

    def _render_list_item_md(self, token: dict) -> str:
        parts = []
        for child in token.get('children', []):
            child_type = child.get('type', '')
            if child_type == 'paragraph':
                parts.append(self._render_inline_md(child.get('children', [])))
            elif child_type == 'list':
                # Nested list: indent
                nested = self._render_list(child)
                for line in nested.split('\n'):
                    parts.append(f'  {line}')
            else:
                rendered = self._render_token(child)
                if rendered:
                    parts.append(rendered)
        return ' '.join(parts)

    def _render_image_md(self, token: dict) -> str:
        src = token.get('attrs', {}).get('url', '')
        alt = token.get('attrs', {}).get('alt', '')
        return f'![{alt}]({src})'

    def _render_table_md(self, token: dict) -> str:
        rows = token.get('children', [])
        if not rows:
            return ''

        lines = []
        for i, row in enumerate(rows):
            if row.get('type') != 'table_row':
                continue
            cells = []
            for cell in row.get('children', []):
                if cell.get('type') in ('table_cell', 'table_head'):
                    cells.append(self._render_inline_md(cell.get('children', [])))
                else:
                    cells.append('')
            lines.append('| ' + ' | '.join(cells) + ' |')
            # Add separator after header row
            if i == 0:
                lines.append('| ' + ' | '.join('---' for _ in cells) + ' |')

        return '\n'.join(lines)

    def _render_inline_md(self, children: list[dict]) -> str:
        """Render inline tokens to Markdown text."""
        parts = []
        for child in children:
            child_type = child.get('type', '')
            if child_type == 'text':
                parts.append(child.get('raw', ''))
            elif child_type == 'strong':
                inner = self._render_inline_md(child.get('children', []))
                parts.append(f'**{inner}**')
            elif child_type == 'emphasis':
                inner = self._render_inline_md(child.get('children', []))
                parts.append(f'*{inner}*')
            elif child_type == 'codespan':
                parts.append(f'`{child.get("raw", "")}`')
            elif child_type == 'link':
                inner = self._render_inline_md(child.get('children', []))
                href = child.get('attrs', {}).get('url', '')
                parts.append(f'[{inner}]({href})')
            elif child_type == 'image':
                src = child.get('attrs', {}).get('url', '')
                alt = child.get('attrs', {}).get('alt', '')
                parts.append(f'![{alt}]({src})')
            elif child_type == 'softbreak':
                parts.append('\n')
            elif child_type == 'linebreak':
                parts.append('  \n')
            elif child_type == 'strikethrough':
                inner = self._render_inline_md(child.get('children', []))
                parts.append(f'~~{inner}~~')
            elif child.get('children'):
                parts.append(self._render_inline_md(child['children']))
            elif 'raw' in child:
                parts.append(child['raw'])
        return ''.join(parts)
