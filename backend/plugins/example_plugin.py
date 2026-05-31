"""示例插件 — 演示如何通过 plugins/ 目录添加新平台。

只需把文件放在 backend/plugins/ 目录下，应用启动时自动发现并注册。
无需修改任何现有代码！

使用方法:
1. 复制此文件重命名为你的平台名, 如 `tieba.py`
2. 修改类名和属性为你的平台信息
3. 重启后端即可在 UI 中看到新平台
"""

from app.platforms.base import PlatformAdapter
from app.transformers.intermediate import ContentAST
from app.utils.html_helpers import wrap_in_html_document


class ExamplePluginPlatform(PlatformAdapter):
    """插件示例：一个自定义平台适配器。

    要自定义你自己的平台，修改以下属性和方法即可。
    """

    @property
    def platform_id(self) -> str:
        return 'plugin_example'

    @property
    def display_name(self) -> str:
        return '示例平台（插件）'

    @property
    def icon(self) -> str:
        return '🧩'

    @property
    def description(self) -> str:
        return '这是一个通过 plugins/ 目录自动注册的示例平台'

    @property
    def content_limits(self) -> dict:
        return {
            'max_title_length': 100,
            'max_body_length': 50000,
            'supports_html': True,
            'supports_markdown': True,
        }

    def transform(self, ast: ContentAST, metadata: dict = None) -> str:
        """将 Markdown AST 转换为平台特定格式。

        这里可以使用 app.transformers.renderers 中的已有渲染器，
        也可以自己实现渲染逻辑。
        """
        # 简单例子：直接输出纯文本
        text_parts = []
        for token in ast.raw_tokens:
            if token.get('type') == 'paragraph':
                children = token.get('children', [])
                for child in children:
                    if child.get('type') == 'text':
                        text_parts.append(child.get('raw', ''))
        return '\n\n'.join(text_parts)

    def generate_preview_html(self, transformed_content: str) -> str:
        """生成用于前端 iframe 预览的完整 HTML 文档。

        可以自定义样式，模拟平台的真实界面效果。
        """
        extra_style = '''
        <style>
            body { max-width: 680px; margin: 0 auto; padding: 20px;
                   font-family: -apple-system, "PingFang SC", sans-serif; }
            .plugin-badge {
                background: linear-gradient(135deg, #667eea, #764ba2);
                color: #fff; padding: 8px 16px; border-radius: 20px;
                display: inline-block; font-size: 13px; margin-bottom: 16px;
            }
        </style>
        '''
        body = f'<div class="plugin-badge">🧩 示例平台预览</div>\n<p>{transformed_content}</p>'
        return wrap_in_html_document(body, title='示例平台预览', extra_head=extra_style)

    def validate(self, transformed_content: str, metadata: dict = None) -> list[dict]:
        """检查内容是否符合平台约束。返回警告列表。"""
        warnings = []
        metadata = metadata or {}
        title = metadata.get('title', '')
        if title and len(title) > 100:
            warnings.append({
                'level': 'error',
                'message': f'标题长度 {len(title)} 超过限制',
                'field': 'title',
            })
        return warnings

    def simulate_publish(self, transformed_content: str, metadata: dict = None) -> dict:
        """模拟发布操作。V1 版本返回格式化内容供用户手动粘贴。"""
        metadata = metadata or {}
        title = metadata.get('title', '未命名')
        return self._make_simulated_result(
            success=True,
            message=f'模拟发布成功："{title[:20]}" 已发布到示例平台',
            extra={
                'content_to_copy': transformed_content,
                'platform_tip': '这是示例平台的模拟发布结果，复制内容到目标编辑器使用',
            },
        )


from app.platforms.registry import registry
registry.register(ExamplePluginPlatform())
