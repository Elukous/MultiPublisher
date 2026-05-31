"""Bilibili column platform adapter."""

from __future__ import annotations

from typing import Any, Optional

from app.platforms.base import PlatformAdapter
from app.transformers.intermediate import ContentAST
from app.transformers.renderers.bilibili_renderer import BilibiliRenderer
from app.utils.html_helpers import wrap_in_html_document


class BilibiliPlatform(PlatformAdapter):

    @property
    def platform_id(self) -> str:
        return 'bilibili'

    @property
    def display_name(self) -> str:
        return 'B站专栏'

    @property
    def icon(self) -> str:
        return '📺'

    @property
    def description(self) -> str:
        return 'Bilibili专栏文章，支持HTML富文本格式'

    @property
    def content_limits(self) -> dict[str, Any]:
        return {
            'max_title_length': 80,
            'supports_html': True,
            'supports_markdown': False,
            'supports_video_embed': True,
        }

    def __init__(self) -> None:
        self._renderer = BilibiliRenderer()

    def transform(self, ast: ContentAST, metadata: Optional[dict] = None) -> str:
        return self._renderer.render(ast, metadata)

    def generate_preview_html(self, transformed_content: str) -> str:
        extra_head = '''
        <style>
            body {
                max-width: 680px; margin: 0 auto; padding: 24px;
                font-family: -apple-system, BlinkMacSystemFont, "Helvetica Neue", "PingFang SC", sans-serif;
            }
            h2, h3, h4 { color: #212121; }
            p { line-height: 1.75; }
            a { color: #00a1d6; }
            blockquote { border-left: 4px solid #00a1d6; padding: 8px 16px; color: #666; background: #f4f5f7; }
            .bili-header {
                background: #00a1d6; color: white; padding: 12px 16px;
                border-radius: 8px 8px 0 0; font-size: 14px;
            }
        </style>
        '''
        body = f'''
        <div class="bili-header">📺 B站专栏预览</div>
        <div style="border:1px solid #e5e5e5; border-top:none; padding:20px; border-radius:0 0 8px 8px;">
            {transformed_content}
        </div>
        '''
        return wrap_in_html_document(body, title='B站专栏预览', extra_head=extra_head)

    def validate(self, transformed_content: str, metadata: Optional[dict] = None) -> list[dict]:
        metadata = metadata or {}
        warnings = []

        title = metadata.get('title', '')
        if title and len(title) > 80:
            warnings.append({
                'level': 'error',
                'message': f'标题长度 {len(title)} 超过B站专栏限制 80 字',
                'field': 'title',
            })

        # Check for script tags
        if '<script' in transformed_content.lower():
            warnings.append({
                'level': 'error',
                'message': '内容中包含 JavaScript，B站专栏不支持',
                'field': 'content',
            })

        return warnings

    def simulate_publish(self, transformed_content: str, metadata: Optional[dict] = None) -> dict:
        metadata = metadata or {}
        title = metadata.get('title', '未命名文章')
        return self._make_simulated_result(
            success=True,
            message=f'模拟发布成功："{title[:20]}" 已发布到B站专栏',
            extra={
                'content_to_copy': transformed_content,
                'platform_tip': '请复制上方 HTML 内容，在B站专栏编辑器中粘贴使用',
            },
        )


from app.platforms.registry import registry  # noqa: E402
registry.register(BilibiliPlatform())
