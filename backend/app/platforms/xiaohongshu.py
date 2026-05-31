"""Xiaohongshu (Little Red Book) platform adapter."""

from __future__ import annotations

import json
from typing import Any, Optional

from app.platforms.base import PlatformAdapter
from app.transformers.intermediate import ContentAST
from app.transformers.renderers.xiaohongshu_renderer import XiaohongshuRenderer
from app.utils.html_helpers import make_preview_phone_frame


class XiaohongshuPlatform(PlatformAdapter):

    @property
    def platform_id(self) -> str:
        return 'xiaohongshu'

    @property
    def display_name(self) -> str:
        return '小红书'

    @property
    def icon(self) -> str:
        return '📕'

    @property
    def description(self) -> str:
        return '小红书笔记，短文本+图片为主，标题限20字，正文限1000字'

    @property
    def content_limits(self) -> dict[str, Any]:
        return {
            'max_title_length': 20,
            'max_body_length': 1000,
            'min_images': 3,
            'max_images': 18,
            'supports_html': False,
            'supports_markdown': False,
            'image_ratio': '3:4',
        }

    def __init__(self) -> None:
        self._renderer = XiaohongshuRenderer()

    def transform(self, ast: ContentAST, metadata: Optional[dict] = None) -> str:
        return self._renderer.render(ast, metadata)

    def generate_preview_html(self, transformed_content: str) -> str:
        try:
            data = json.loads(transformed_content)
        except json.JSONDecodeError:
            data = {'title': '', 'body': transformed_content}

        title = data.get('title', '')
        body = data.get('body_with_emoji') or data.get('body', '')
        tags = data.get('suggested_tags', [])
        warnings = data.get('image_warnings', [])
        char_info = f"字数: {data.get('char_count', 0)}/{data.get('char_limit', 1000)}"

        body_html = body.replace('\n', '<br>')

        tags_html = ' '.join(
            f'<span style="color:#ff2442; font-size:13px;">{tag}</span>'
            for tag in tags
        )

        warnings_html = ''
        if warnings:
            items = ''.join(f'<li>⚠️ {w}</li>' for w in warnings)
            warnings_html = f'<ul style="color:#ff6600; font-size:12px; margin:8px 0;">{items}</ul>'

        card = f'''
        <div style="padding:16px; font-family:-apple-system,sans-serif;">
            <h2 style="font-size:17px; font-weight:bold; margin:0 0 10px 0; color:#333;">{title}</h2>
            <p style="font-size:14px; line-height:1.8; color:#333; margin:0 0 10px 0;">{body_html}</p>
            <div style="margin:8px 0;">{tags_html}</div>
            <div style="font-size:12px; color:#999; margin:4px 0;">{char_info}</div>
            {warnings_html}
        </div>
        '''
        return make_preview_phone_frame(card, title='小红书预览')

    def validate(self, transformed_content: str, metadata: Optional[dict] = None) -> list[dict]:
        warnings = []
        try:
            data = json.loads(transformed_content)
        except json.JSONDecodeError:
            return [{'level': 'error', 'message': '内容解析失败', 'field': 'content'}]

        title = data.get('title', '')
        if len(title) > 20:
            warnings.append({
                'level': 'error',
                'message': f'标题 {len(title)} 字超过小红书 20 字限制',
                'field': 'title',
            })

        if data.get('char_count', 0) > data.get('char_limit', 1000):
            warnings.append({
                'level': 'warning',
                'message': f"正文 {data['char_count']} 字超过 {data['char_limit']} 字限制，已截断",
                'field': 'body',
            })

        for img_warn in data.get('image_warnings', []):
            warnings.append({
                'level': 'warning',
                'message': img_warn,
                'field': 'images',
            })

        for content_warn in data.get('warnings', []):
            warnings.append({
                'level': 'warning',
                'message': content_warn,
                'field': 'content',
            })

        return warnings

    def simulate_publish(self, transformed_content: str, metadata: Optional[dict] = None) -> dict:
        metadata = metadata or {}
        title = metadata.get('title', '未命名笔记')
        try:
            data = json.loads(transformed_content)
            body_for_copy = data.get('body_with_emoji') or data.get('body', '')
            tags = ' '.join(data.get('suggested_tags', []))
            copy_content = f"{data.get('title', title)}\n\n{body_for_copy}\n\n{tags}"
        except json.JSONDecodeError:
            copy_content = transformed_content

        return self._make_simulated_result(
            success=True,
            message=f'模拟发布成功："{title[:20]}" 已发布到小红书',
            extra={
                'content_to_copy': copy_content,
                'platform_tip': '请复制上方内容，在小红书 APP 中粘贴发布。图片需单独上传。',
            },
        )


from app.platforms.registry import registry  # noqa: E402
registry.register(XiaohongshuPlatform())
