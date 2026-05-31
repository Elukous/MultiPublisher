from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ContentAST:
    """Canonical intermediate representation of article content.

    Constructed from mistune AST tokens. All platform renderers consume
    this single structure to produce platform-specific output.
    """

    raw_tokens: list[dict]
    title: Optional[str] = None
    headings: list[dict] = field(default_factory=list)
    images: list[str] = field(default_factory=list)
    links: list[str] = field(default_factory=list)
    word_count: int = 0
    has_code_blocks: bool = False
    has_tables: bool = False

    @classmethod
    def from_tokens(
        cls, tokens: list[dict], title: Optional[str] = None
    ) -> ContentAST:
        """Construct ContentAST from mistune AST tokens, extracting metadata."""
        ast = cls(raw_tokens=tokens)
        ast._extract_metadata(title)
        return ast

    def _extract_metadata(self, title: Optional[str] = None) -> None:
        """Walk the token tree and extract headings, images, links, etc."""
        if title:
            self.title = title

        text_parts: list[str] = []
        self._walk_tokens(self.raw_tokens, text_parts)
        self.word_count = len(re.findall(r'[\w一-鿿]+', ' '.join(text_parts)))

        # If no title was provided, use the first heading
        if not self.title and self.headings:
            self.title = self.headings[0].get('text', '')

    def _walk_tokens(self, tokens: list[dict], text_parts: list[str]) -> None:
        """Recursively walk tokens to extract metadata."""
        for token in tokens:
            token_type = token.get('type', '')
            children = token.get('children', [])

            if token_type == 'heading':
                level = token.get('attrs', {}).get('level', 1)
                text = self._get_inline_text(children)
                self.headings.append({'level': level, 'text': text})
                text_parts.append(text)

            elif token_type == 'paragraph':
                text_parts.append(self._get_inline_text(children))

            elif token_type == 'block_code':
                self.has_code_blocks = True
                text_parts.append(token.get('raw', ''))

            elif token_type == 'table':
                self.has_tables = True

            elif token_type == 'image':
                src = ''
                for child in children:
                    if child.get('type') == 'image':
                        src = child.get('attrs', {}).get('url', '')
                        if src:
                            self.images.append(src)
                if not src:
                    # Direct image token (not wrapped)
                    src = token.get('attrs', {}).get('url', '')
                    if src:
                        self.images.append(src)

            elif token_type == 'list':
                for child in children:
                    self._walk_tokens(child.get('children', []), text_parts)

            elif token_type == 'block_quote':
                self._walk_tokens(children, text_parts)

            elif token_type == 'thematic_break':
                pass  # No content to extract

            else:
                # Generic: walk children if present
                if children:
                    self._walk_tokens(children, text_parts)

    def _get_inline_text(self, children: list[dict]) -> str:
        """Extract plain text from inline children (text, strong, emphasis, etc.)."""
        parts = []
        for child in children:
            child_type = child.get('type', '')
            if child_type == 'text':
                parts.append(child.get('raw', ''))
            elif child_type in ('strong', 'emphasis', 'strikethrough'):
                parts.append(self._get_inline_text(child.get('children', [])))
            elif child_type == 'link':
                href = child.get('attrs', {}).get('url', '')
                if href:
                    self.links.append(href)
                parts.append(self._get_inline_text(child.get('children', [])))
            elif child_type == 'image':
                src = child.get('attrs', {}).get('url', '')
                if src:
                    self.images.append(src)
                alt = child.get('attrs', {}).get('alt', '')
                parts.append(alt)
            elif child_type == 'codespan':
                parts.append(child.get('raw', ''))
            elif child.get('children'):
                parts.append(self._get_inline_text(child['children']))
            elif 'raw' in child:
                parts.append(child['raw'])
        return ''.join(parts)

    def get_text_content(self) -> str:
        """Extract all plain text from the AST."""
        parts: list[str] = []
        self._walk_tokens(self.raw_tokens, parts)
        return ' '.join(parts)

    def get_sections(self) -> list[dict]:
        """Break content into sections by heading.

        Returns a list of dicts, each with 'heading' (str or None) and
        'tokens' (list of token dicts belonging to that section).
        """
        sections: list[dict] = []
        current_section_tokens: list[dict] = []
        current_heading: Optional[str] = None

        for token in self.raw_tokens:
            if token.get('type') == 'heading':
                # Save previous section
                if current_section_tokens:
                    sections.append({
                        'heading': current_heading,
                        'tokens': current_section_tokens,
                    })
                current_heading = self._get_inline_text(
                    token.get('children', [])
                )
                current_section_tokens = [token]
            else:
                current_section_tokens.append(token)

        # Don't forget the last section
        if current_section_tokens:
            sections.append({
                'heading': current_heading,
                'tokens': current_section_tokens,
            })

        return sections
