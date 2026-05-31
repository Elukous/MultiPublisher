#!/usr/bin/env python3
"""CLI scaffolding tool — generates boilerplate code for a new platform plugin.

Usage:
    python scaffold_plugin.py my_platform "My Platform" 🎯

This creates backend/plugins/my_platform.py with a complete PlatformAdapter template.
"""

import sys
from pathlib import Path


TEMPLATE = '''"""<name> platform plugin — auto-generated.

Place this file in backend/plugins/ and restart the server.
The platform will appear automatically in the UI.
"""

from app.platforms.base import PlatformAdapter
from app.transformers.intermediate import ContentAST
from app.transformers.renderers.wechat_renderer import WeChatRenderer
from app.utils.html_helpers import wrap_in_html_document


class <class_name>(PlatformAdapter):
    """<name> platform adapter."""

    @property
    def platform_id(self) -> str:
        return '<id>'

    @property
    def display_name(self) -> str:
        return '<display_name>'

    @property
    def icon(self) -> str:
        return '<icon>'

    @property
    def description(self) -> str:
        return '<name>平台适配器'

    @property
    def content_limits(self) -> dict:
        return {
            'max_title_length': 100,
            'max_body_length': 50000,
            'supports_html': True,
        }

    def __init__(self):
        # 你可以使用内置的渲染器，或者创建自己的渲染器
        # 可选: WeChatRenderer, ZhihuRenderer, BilibiliRenderer, XiaohongshuRenderer
        self._renderer = WeChatRenderer()

    def transform(self, ast: ContentAST, metadata: dict = None) -> str:
        """将 Markdown 内容转换为平台特定格式。"""
        return self._renderer.render(ast, metadata)

    def generate_preview_html(self, transformed_content: str) -> str:
        """生成前端 iframe 预览的完整 HTML。"""
        extra_style = '''
        <style>
            body {{
                max-width: 720px; margin: 0 auto; padding: 20px;
                font-family: -apple-system, "PingFang SC", sans-serif;
            }}
            .platform-header {{
                background: #667eea; color: white; padding: 8px 16px;
                border-radius: 8px 8px 0 0; font-size: 14px;
            }}
        </style>
        '''
        body = f'<div class="platform-header">{self.icon} {self.display_name} 预览</div>\\n<div>{transformed_content}</div>'
        return wrap_in_html_document(body, title='<name> 预览', extra_head=extra_style)

    def validate(self, transformed_content: str, metadata: dict = None) -> list[dict]:
        """检查内容是否符合平台约束。"""
        warnings = []
        metadata = metadata or {}
        max_title = self.content_limits.get('max_title_length', 0)
        title = metadata.get('title', '')
        if max_title and len(title) > max_title:
            warnings.append({{
                'level': 'error',
                'message': f'标题长度 {{len(title)}} 超过限制 {{max_title}}',
                'field': 'title',
            }})
        return warnings

    def simulate_publish(self, transformed_content: str, metadata: dict = None) -> dict:
        """模拟发布到平台。"""
        metadata = metadata or {}
        title = metadata.get('title', '未命名')
        return self._make_simulated_result(
            success=True,
            message=f'模拟发布成功："{{title[:20]}}" 已发布到 {self.display_name}',
            extra={{
                'content_to_copy': transformed_content,
                'platform_tip': '请复制上述内容，在目标平台编辑器中粘贴使用',
            }},
        )


from app.platforms.registry import registry
registry.register(<class_name>())
'''


def to_pascal_case(s: str) -> str:
    """Convert snake_case or space-separated to PascalCase."""
    import re
    parts = re.split(r'[ _-]', s)
    return ''.join(p.capitalize() for p in parts)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    platform_id = sys.argv[1]
    display_name = sys.argv[2] if len(sys.argv) > 2 else platform_id.replace('_', ' ').title()
    icon = sys.argv[3] if len(sys.argv) > 3 else '🔌'

    class_name = to_pascal_case(platform_id) + 'Platform'
    plugins_dir = Path(__file__).parent / 'plugins'
    output_path = plugins_dir / f'{platform_id}.py'

    content = TEMPLATE
    content = content.replace('<id>', platform_id)
    content = content.replace('<name>', display_name)
    content = content.replace('<display_name>', display_name)
    content = content.replace('<icon>', icon)
    content = content.replace('<class_name>', class_name)

    output_path.write_text(content, encoding='utf-8')
    print(f'✅ 平台插件已创建: {output_path}')
    print(f'   类名: {class_name}')
    print(f'   平台ID: {platform_id}')
    print(f'   显示名: {display_name}')
    print(f'   图标: {icon}')
    print()
    print(f'重启后端后即可在 UI 中看到 "{display_name}" 平台。')
    print(f'或运行: uvicorn app.main:app --reload')


if __name__ == '__main__':
    main()
