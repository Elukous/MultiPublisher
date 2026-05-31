"""WeChat Official Account platform adapter."""

from __future__ import annotations

from typing import Any, Optional

from app.platforms.base import PlatformAdapter
from app.transformers.intermediate import ContentAST
from app.transformers.renderers.wechat_renderer import WeChatRenderer
from app.utils.html_helpers import make_preview_phone_frame


class WeChatPlatform(PlatformAdapter):

    @property
    def platform_id(self) -> str:
        return 'wechat'

    @property
    def display_name(self) -> str:
        return '微信公众号'

    @property
    def icon(self) -> str:
        return '💬'

    @property
    def description(self) -> str:
        return '微信公众号图文消息，需要全内联样式HTML'

    @property
    def content_limits(self) -> dict[str, Any]:
        return {
            'max_title_length': 64,
            'supports_html': True,
            'supports_markdown': False,
            'inline_styles_required': True,
            'max_image_size_mb': 10,
        }

    def __init__(self) -> None:
        self._renderer = WeChatRenderer()

    def transform(self, ast: ContentAST, metadata: Optional[dict] = None) -> str:
        return self._renderer.render(ast, metadata)

    def generate_preview_html(self, transformed_content: str) -> str:
        return make_preview_phone_frame(transformed_content, title='微信公众号预览')

    def validate(self, transformed_content: str, metadata: Optional[dict] = None) -> list[dict]:
        metadata = metadata or {}
        warnings = []

        # Check title length
        title = metadata.get('title', '')
        if title and len(title) > 64:
            warnings.append({
                'level': 'error',
                'message': f'标题长度 {len(title)} 超过微信限制 64 字',
                'field': 'title',
            })

        # Check for external images (WeChat may not display them)
        if 'http' in transformed_content and '<img' in transformed_content:
            import re
            external_imgs = re.findall(r'<img[^>]+src="https?://[^"]*"', transformed_content)
            if external_imgs:
                warnings.append({
                    'level': 'warning',
                    'message': f'检测到 {len(external_imgs)} 张外链图片，微信公众号可能无法显示外链图片，建议上传到微信图床',
                    'field': 'images',
                })

        # Check for <style> tags (WeChat strips them)
        if '<style' in transformed_content:
            warnings.append({
                'level': 'error',
                'message': '内容中包含 <style> 标签，微信公众号会将其移除，请使用内联样式',
                'field': 'content',
            })

        # Check for JavaScript
        if '<script' in transformed_content.lower():
            warnings.append({
                'level': 'error',
                'message': '内容中包含 JavaScript，微信公众号不支持',
                'field': 'content',
            })

        return warnings

    def simulate_publish(self, transformed_content: str, metadata: Optional[dict] = None) -> dict:
        metadata = metadata or {}
        title = metadata.get('title', '未命名文章')
        return self._make_simulated_result(
            success=True,
            message=f'模拟发布成功："{title[:20]}" 已发布到微信公众号',
            extra={
                'content_to_copy': transformed_content,
                'platform_tip': '请复制上方 HTML 内容，在微信公众号编辑器中粘贴使用',
            },
        )


from app.platforms.registry import registry  # noqa: E402
registry.register(WeChatPlatform())
