"""Tests for all four platform renderers."""

import json

from app.transformers.parser import parse_markdown
from app.transformers.intermediate import ContentAST
from app.transformers.renderers.wechat_renderer import WeChatRenderer
from app.transformers.renderers.zhihu_renderer import ZhihuRenderer
from app.transformers.renderers.xiaohongshu_renderer import XiaohongshuRenderer
from app.transformers.renderers.bilibili_renderer import BilibiliRenderer


SAMPLE_MD = """# 测试标题

这是正文段落，包含**加粗**和*斜体*。

## 代码部分

```python
print("hello")
```

- 列表项1
- 列表项2

> 引用文字

![图片](https://example.com/img.png)
"""


def _make_ast(md: str = SAMPLE_MD) -> ContentAST:
    tokens = parse_markdown(md)
    return ContentAST.from_tokens(tokens, title='测试标题')


class TestWeChatRenderer:
    def test_renders_html(self):
        renderer = WeChatRenderer()
        html = renderer.render(_make_ast())
        assert '<section style=' in html
        assert 'PingFang SC' in html

    def test_heading_styles(self):
        renderer = WeChatRenderer()
        html = renderer.render(_make_ast())
        assert 'font-size:22px' in html
        assert 'border-bottom:2px solid #3eaf7c' in html

    def test_inline_styles(self):
        renderer = WeChatRenderer()
        html = renderer.render(_make_ast())
        # Bold should have inline style
        assert '<strong style=' in html
        # Code inline should have background
        assert 'background:#f0f0f0' in html or 'background:#282c34' in html

    def test_code_block_rendered(self):
        renderer = WeChatRenderer()
        html = renderer.render(_make_ast())
        assert '<pre>' in html
        assert 'background:#282c34' in html

    def test_list_rendered(self):
        renderer = WeChatRenderer()
        html = renderer.render(_make_ast())
        assert '<ul style=' in html or '<li style=' in html

    def test_blockquote_rendered(self):
        renderer = WeChatRenderer()
        html = renderer.render(_make_ast())
        assert '<blockquote style=' in html

    def test_image_rendered(self):
        renderer = WeChatRenderer()
        html = renderer.render(_make_ast())
        assert '<img src=' in html
        assert 'example.com/img.png' in html


class TestZhihuRenderer:
    def test_renders_markdown(self):
        renderer = ZhihuRenderer()
        md = renderer.render(_make_ast())
        assert isinstance(md, str)
        assert len(md) > 0

    def test_headings_start_from_h2(self):
        renderer = ZhihuRenderer()
        md = renderer.render(_make_ast())
        # Original H1 should become ## (Zhihu convention)
        lines = md.split('\n')
        h_lines = [l for l in lines if l.startswith('#')]
        for h in h_lines:
            assert h.startswith('##'), f"Heading should start from ##, got: {h}"

    def test_preserves_bold(self):
        renderer = ZhihuRenderer()
        md = renderer.render(_make_ast())
        assert '**' in md

    def test_preserves_code_block(self):
        renderer = ZhihuRenderer()
        md = renderer.render(_make_ast())
        assert '```' in md

    def test_preserves_list(self):
        renderer = ZhihuRenderer()
        md = renderer.render(_make_ast())
        assert '- ' in md

    def test_preserves_image(self):
        renderer = ZhihuRenderer()
        md = renderer.render(_make_ast())
        assert '![' in md
        assert 'example.com/img.png' in md


class TestXiaohongshuRenderer:
    def test_renders_json(self):
        renderer = XiaohongshuRenderer()
        result = renderer.render(_make_ast())
        data = json.loads(result)
        assert 'title' in data
        assert 'body' in data

    def test_title_under_limit(self):
        renderer = XiaohongshuRenderer()
        result = renderer.render(_make_ast())
        data = json.loads(result)
        assert len(data['title']) <= 20

    def test_suggests_tags(self):
        renderer = XiaohongshuRenderer()
        result = renderer.render(_make_ast())
        data = json.loads(result)
        assert isinstance(data['suggested_tags'], list)

    def test_suggests_emojis(self):
        renderer = XiaohongshuRenderer()
        result = renderer.render(_make_ast())
        data = json.loads(result)
        assert isinstance(data['emoji_suggestions'], list)
        assert len(data['emoji_suggestions']) > 0

    def test_image_warnings(self):
        renderer = XiaohongshuRenderer()
        result = renderer.render(_make_ast())
        data = json.loads(result)
        assert isinstance(data['image_warnings'], list)

    def test_code_block_warning(self):
        renderer = XiaohongshuRenderer()
        result = renderer.render(_make_ast())
        data = json.loads(result)
        assert any('代码块' in w for w in data.get('warnings', []))


class TestBilibiliRenderer:
    def test_renders_html(self):
        renderer = BilibiliRenderer()
        html = renderer.render(_make_ast())
        assert '<h2' in html or '<h3' in html
        assert '<p' in html

    def test_code_with_language_class(self):
        renderer = BilibiliRenderer()
        html = renderer.render(_make_ast())
        assert 'language-python' in html

    def test_strong_and_em(self):
        renderer = BilibiliRenderer()
        html = renderer.render(_make_ast())
        assert '<strong>' in html
        assert '<em>' in html

    def test_list_rendered(self):
        renderer = BilibiliRenderer()
        html = renderer.render(_make_ast())
        assert '<ul>' in html or '<ol>' in html

    def test_blockquote_rendered(self):
        renderer = BilibiliRenderer()
        html = renderer.render(_make_ast())
        assert '<blockquote' in html

    def test_image_rendered(self):
        renderer = BilibiliRenderer()
        html = renderer.render(_make_ast())
        assert '<img src=' in html
