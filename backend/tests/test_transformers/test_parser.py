"""Tests for the markdown parser."""

from app.transformers.parser import parse_markdown
from app.transformers.intermediate import ContentAST


class TestParser:
    def test_parse_heading(self):
        tokens = parse_markdown('# Hello World')
        headings = [t for t in tokens if t.get('type') == 'heading']
        assert len(headings) >= 1

    def test_parse_paragraph(self):
        tokens = parse_markdown('This is a paragraph.')
        paras = [t for t in tokens if t.get('type') == 'paragraph']
        assert len(paras) >= 1

    def test_parse_code_block(self):
        tokens = parse_markdown('```\ncode here\n```')
        code_blocks = [t for t in tokens if t.get('type') == 'block_code']
        assert len(code_blocks) >= 1

    def test_parse_list(self):
        tokens = parse_markdown('- Item 1\n- Item 2')
        lists = [t for t in tokens if t.get('type') == 'list']
        assert len(lists) >= 1

    def test_parse_empty(self):
        tokens = parse_markdown('')
        assert isinstance(tokens, list)


class TestContentAST:
    def test_from_tokens_basic(self):
        tokens = parse_markdown('# Title\n\nParagraph text here.')
        ast = ContentAST.from_tokens(tokens, title='Title')
        assert ast.title == 'Title'
        assert ast.word_count > 0

    def test_from_tokens_extracts_title(self):
        tokens = parse_markdown('# My Heading\n\nSome content.')
        ast = ContentAST.from_tokens(tokens)
        assert ast.title == 'My Heading'

    def test_from_tokens_detects_code_blocks(self):
        tokens = parse_markdown('```\ncode\n```')
        ast = ContentAST.from_tokens(tokens)
        assert ast.has_code_blocks is True

    def test_from_tokens_no_code_blocks(self):
        tokens = parse_markdown('Just text here.')
        ast = ContentAST.from_tokens(tokens)
        assert ast.has_code_blocks is False

    def test_get_text_content(self):
        tokens = parse_markdown('# Title\n\nHello **world**.')
        ast = ContentAST.from_tokens(tokens)
        text = ast.get_text_content()
        assert 'Title' in text
        assert 'Hello' in text

    def test_get_sections(self):
        tokens = parse_markdown('# Section 1\n\nText 1.\n\n# Section 2\n\nText 2.')
        ast = ContentAST.from_tokens(tokens)
        sections = ast.get_sections()
        assert len(sections) >= 2

    def test_images_extracted(self):
        tokens = parse_markdown('![alt](https://example.com/img.png)')
        ast = ContentAST.from_tokens(tokens)
        assert 'https://example.com/img.png' in ast.images
