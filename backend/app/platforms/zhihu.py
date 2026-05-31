"""Zhihu platform adapter."""

from __future__ import annotations

from typing import Any, Optional

from app.platforms.base import PlatformAdapter
from app.transformers.intermediate import ContentAST
from app.transformers.renderers.zhihu_renderer import ZhihuRenderer
from app.utils.html_helpers import wrap_in_html_document


class ZhihuPlatform(PlatformAdapter):

    @property
    def platform_id(self) -> str:
        return 'zhihu'

    @property
    def display_name(self) -> str:
        return '知乎'

    @property
    def icon(self) -> str:
        return '🔍'

    @property
    def description(self) -> str:
        return '知乎专栏文章，支持 Markdown 格式'

    @property
    def content_limits(self) -> dict[str, Any]:
        return {
            'max_title_length': 100,
            'supports_html': False,
            'supports_markdown': True,
            'supports_latex': True,
        }

    def __init__(self) -> None:
        self._renderer = ZhihuRenderer()

    def transform(self, ast: ContentAST, metadata: Optional[dict] = None) -> str:
        return self._renderer.render(ast, metadata)

    def generate_preview_html(self, transformed_content: str) -> str:
        # Render Markdown preview as rendered HTML in an iframe
        import mistune
        md_html = mistune.html(transformed_content)
        extra_head = '''
        <style>
            body { max-width: 720px; margin: 0 auto; padding: 20px; font-family: -apple-system, BlinkMacSystemFont, "Helvetica Neue", "PingFang SC", "Microsoft YaHei", sans-serif; }
            h2 { font-size: 22px; font-weight: bold; margin: 24px 0 12px; }
            h3 { font-size: 19px; font-weight: bold; margin: 20px 0 10px; }
            p { font-size: 15px; line-height: 1.8; color: #333; margin: 12px 0; }
            code { background: #f0f0f0; padding: 2px 6px; border-radius: 3px; font-size: 90%; }
            pre { background: #f6f8fa; padding: 16px; border-radius: 6px; overflow-x: auto; }
            pre code { background: none; padding: 0; }
            blockquote { border-left: 4px solid #0066ff; padding: 8px 16px; color: #666; margin: 12px 0; }
            img { max-width: 100%; }
            a { color: #0066ff; }
        </style>
        '''
        return wrap_in_html_document(md_html, title='知乎预览', extra_head=extra_head)

    def validate(self, transformed_content: str, metadata: Optional[dict] = None) -> list[dict]:
        metadata = metadata or {}
        warnings = []

        title = metadata.get('title', '')
        if title and len(title) > 100:
            warnings.append({
                'level': 'error',
                'message': f'标题长度 {len(title)} 超过知乎限制 100 字',
                'field': 'title',
            })

        # Check heading levels (should start from ##)
        import re
        h1_matches = re.findall(r'^# [^#]', transformed_content, re.MULTILINE)
        if h1_matches:
            warnings.append({
                'level': 'warning',
                'message': f'检测到 {len(h1_matches)} 个一级标题，知乎文章标题即为 H1，建议从 ## 开始',
                'field': 'content',
            })

        return warnings

    def simulate_publish(self, transformed_content: str, metadata: Optional[dict] = None) -> dict:
        metadata = metadata or {}
        title = metadata.get('title', '未命名文章')
        return self._make_simulated_result(
            success=True,
            message=f'模拟发布成功："{title[:20]}" 已发布到知乎专栏',
            extra={
                'content_to_copy': transformed_content,
                'platform_tip': '请复制上方 Markdown 内容，在知乎专栏编辑器中粘贴使用',
            },
        )


from app.platforms.registry import registry  # noqa: E402
registry.register(ZhihuPlatform())
