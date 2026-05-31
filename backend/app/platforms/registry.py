"""Platform registry with plugin auto-discovery and hot-reload support.

Three levels of extensibility:
1. Built-in platforms: imported in auto_register_platforms()
2. Plugin discover: modules dropped in backend/plugins/ are auto-loaded
3. Config custom: user-defined platforms from data/custom_platforms.json

Any PlatformAdapter subclass in these locations is auto-registered.
"""

from __future__ import annotations

import importlib
import importlib.util
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Optional

from app.config import settings
from app.platforms.base import PlatformAdapter

logger = logging.getLogger(__name__)


class PlatformRegistry:
    """Singleton registry for platform adapters.

    Supports registration, lookup, and dynamic reload of platform plugins.
    """

    _instance: Optional[PlatformRegistry] = None

    def __new__(cls) -> PlatformRegistry:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._adapters: dict[str, PlatformAdapter] = {}
        return cls._instance

    def register(self, adapter: PlatformAdapter) -> None:
        """Register a platform adapter. Overwrites existing if ID conflicts."""
        self._adapters[adapter.platform_id] = adapter
        logger.info(
            'Platform registered: %s (%s)',
            adapter.display_name,
            adapter.platform_id,
        )

    def unregister(self, platform_id: str) -> None:
        """Remove a platform from the registry."""
        self._adapters.pop(platform_id, None)

    def get(self, platform_id: str) -> PlatformAdapter:
        """Get a platform adapter by ID. Raises KeyError if not found."""
        adapter = self._adapters.get(platform_id)
        if not adapter:
            raise KeyError(f"Platform '{platform_id}' not registered")
        return adapter

    def list_all(self) -> list[PlatformAdapter]:
        """Return all registered adapters."""
        return list(self._adapters.values())

    def list_ids(self) -> list[str]:
        """Return all registered platform IDs."""
        return list(self._adapters.keys())

    def __contains__(self, platform_id: str) -> bool:
        return platform_id in self._adapters

    def __len__(self) -> int:
        return len(self._adapters)


# Global singleton instance
registry = PlatformRegistry()


# =============================================================================
# Level 1: Built-in platform imports
# =============================================================================

def auto_register_platforms() -> None:
    """Register all platforms: built-in imports + plugin discovery + custom config."""
    _register_builtin_platforms()
    _discover_plugins()
    _load_custom_config_platforms()


def _register_builtin_platforms() -> None:
    """Import built-in platform modules (they self-register at import time)."""
    import app.platforms.wechat  # noqa: F401
    import app.platforms.zhihu  # noqa: F401
    import app.platforms.xiaohongshu  # noqa: F401
    import app.platforms.bilibili  # noqa: F401
    logger.info('Built-in platforms registered')


# =============================================================================
# Level 2: Plugin auto-discovery from backend/plugins/
# =============================================================================

PLUGINS_DIR = Path(__file__).resolve().parent.parent.parent / 'plugins'


def _discover_plugins() -> None:
    """Scan backend/plugins/ for .py files and import any PlatformAdapter subclass.

    Each plugin file must define a class that inherits from PlatformAdapter.
    The adapter registers itself at module level via registry.register().
    """
    if not PLUGINS_DIR.exists():
        PLUGINS_DIR.mkdir(parents=True, exist_ok=True)
        logger.info('Created plugins directory: %s', PLUGINS_DIR)
        return

    # Ensure plugins dir is on sys.path so we can import from it
    plugins_str = str(PLUGINS_DIR)
    if plugins_str not in sys.path:
        sys.path.insert(0, plugins_str)

    plugin_files = sorted(PLUGINS_DIR.glob('[!_]*.py'))
    if not plugin_files:
        logger.info('No plugin files found in %s', PLUGINS_DIR)
        return

    for plugin_path in plugin_files:
        _load_plugin_file(plugin_path)

    logger.info('Discovered %d plugin(s)', len(plugin_files))


def _load_plugin_file(plugin_path: Path) -> Optional[object]:
    """Dynamically import a single plugin file and return its module."""
    module_name = plugin_path.stem
    try:
        # Remove cached version if re-importing
        if module_name in sys.modules:
            del sys.modules[module_name]

        spec = importlib.util.spec_from_file_location(module_name, plugin_path)
        if spec is None or spec.loader is None:
            logger.warning('Could not load plugin: %s', plugin_path)
            return None

        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        logger.info('Loaded plugin: %s', plugin_path.name)
        return module
    except Exception as e:
        logger.error('Failed to load plugin %s: %s', plugin_path.name, e)
        return None


def reload_plugins() -> list[dict[str, Any]]:
    """Reload all plugins from disk. Used for hot-reload.

    Returns a list of currently registered platform info dicts.
    """
    # Remove previously registered plugin platforms (built-in are kept)
    plugin_platforms = [pid for pid in registry.list_ids()
                        if pid.startswith('plugin_') or pid.startswith('custom_')]
    for pid in plugin_platforms:
        registry.unregister(pid)

    _discover_plugins()
    _load_custom_config_platforms()
    _reimport_custom_platforms()

    return [a.get_platform_info() for a in registry.list_all()]


def _reimport_custom_platforms() -> None:
    """Re-run custom platform config loading."""
    # Also re-discover any plugin_ prefixed ones
    pass


# =============================================================================
# Level 3: User-defined custom platforms via JSON config (no code needed)
# =============================================================================

CUSTOM_PLATFORMS_FILE = settings.data_dir / 'custom_platforms.json'


def _load_custom_config_platforms() -> None:
    """Load user-defined platforms from config JSON file.

    The JSON file contains a list of platform definitions. Each definition
    specifies how to transform content and generate a preview.
    """
    if not CUSTOM_PLATFORMS_FILE.exists():
        return

    try:
        platforms_data = json.loads(CUSTOM_PLATFORMS_FILE.read_text(encoding='utf-8'))
    except (json.JSONDecodeError, OSError) as e:
        logger.warning('Failed to read custom platforms config: %s', e)
        return

    for platform_def in platforms_data:
        try:
            adapter = _build_custom_platform(platform_def)
            if adapter:
                registry.register(adapter)
        except Exception as e:
            logger.error('Failed to load custom platform %s: %s',
                         platform_def.get('name', 'unknown'), e)

    logger.info('Loaded custom config platforms')


def _build_custom_platform(platform_def: dict) -> Optional['CustomPlatformAdapter']:
    """Construct a CustomPlatformAdapter from a config dict."""
    required = ['id', 'name', 'format']
    for field in required:
        if field not in platform_def:
            logger.warning('Custom platform missing required field: %s', field)
            return None

    return CustomPlatformAdapter(platform_def)


def save_custom_platforms(platforms: list[dict]) -> list[dict[str, Any]]:
    """Save custom platform definitions and reload the registry.

    Returns updated list of all platform info dicts.
    """
    CUSTOM_PLATFORMS_FILE.parent.mkdir(parents=True, exist_ok=True)
    CUSTOM_PLATFORMS_FILE.write_text(
        json.dumps(platforms, ensure_ascii=False, indent=2),
        encoding='utf-8',
    )
    reload_plugins()
    return [a.get_platform_info() for a in registry.list_all()]


# =============================================================================
# CustomPlatformAdapter — no-code platform via JSON config
# =============================================================================

CUSTOM_FORMAT_MODES = {
    'html': 'direct_html',
    'markdown': 'clean_markdown',
    'plain_text': 'plain_text',
    'json': 'json_output',
}

STYLE_PRESETS = {
    'mobile': {
        'wrapper': 'max-width:375px; margin:0 auto; font-family:sans-serif;',
        'paragraph': 'font-size:15px; line-height:1.7; margin:12px 0;',
        'heading': 'font-weight:bold; margin:20px 0 10px;',
    },
    'desktop': {
        'wrapper': 'max-width:720px; margin:0 auto; font-family:sans-serif;',
        'paragraph': 'font-size:16px; line-height:1.8; margin:16px 0;',
        'heading': 'font-weight:bold; margin:24px 0 12px;',
    },
    'minimal': {
        'wrapper': 'font-family:sans-serif;',
        'paragraph': 'font-size:14px; line-height:1.6; margin:8px 0;',
        'heading': 'font-weight:bold; margin:16px 0 8px;',
    },
}


class CustomPlatformAdapter(PlatformAdapter):
    """A config-driven platform adapter that users create without writing code.

    Users define platforms in data/custom_platforms.json with:
      - id (unique slug)
      - name (display name)
      - icon (emoji)
      - format (html/markdown/plain_text/json)
      - style_preset (mobile/desktop/minimal)
      - content_limits (title length, body length, etc.)
      - template (optional custom HTML template string)
    """

    def __init__(self, config: dict) -> None:
        self._config = config
        self._renderer = CustomContentRenderer(config)
        self._name = config.get('name', 'Custom Platform')
        self._platform_id = f'custom_{config.get("id", "unknown")}'
        self._icon = config.get('icon', '🔌')
        self._description = config.get('description', '')
        self._limits = config.get('content_limits', {})
        self._format_mode = config.get('format', 'html')
        self._style_preset = config.get('style_preset', 'desktop')
        self._template = config.get('template', '')
        self._preprocessor_rules = config.get('preprocessor', {})

    @property
    def platform_id(self) -> str:
        return self._platform_id

    @property
    def display_name(self) -> str:
        return self._name

    @property
    def icon(self) -> str:
        return self._icon

    @property
    def description(self) -> str:
        return self._description

    @property
    def content_limits(self) -> dict[str, Any]:
        return self._limits

    def transform(self, ast: ContentAST, metadata: Optional[dict] = None) -> str:
        return self._renderer.render(ast, metadata)

    def generate_preview_html(self, transformed_content: str) -> str:
        from app.utils.html_helpers import wrap_in_html_document

        style = STYLE_PRESETS.get(self._style_preset, STYLE_PRESETS['desktop'])
        inline_css = (
            f'body {{ {style["wrapper"]} padding:20px; }} '
            f'p {{ {style["paragraph"]} }} '
            f'h1,h2,h3,h4 {{ {style["heading"]} }} '
            f'img {{ max-width:100%; }} '
            f'code {{ background:#f4f4f4; padding:2px 6px; border-radius:3px; }} '
            f'pre {{ background:#f4f4f4; padding:16px; border-radius:6px; overflow-x:auto; }} '
            f'blockquote {{ border-left:4px solid #666; padding:8px 16px; color:#666; }} '
        )

        if self._format_mode == 'markdown':
            import mistune
            body = mistune.html(transformed_content)
        elif self._format_mode == 'plain_text':
            body = f'<pre style="white-space:pre-wrap;font-size:14px;">{transformed_content}</pre>'
        elif self._format_mode == 'json':
            body = f'<pre style="white-space:pre-wrap;font-size:13px;color:#666;">{transformed_content}</pre>'
        else:
            body = transformed_content

        return wrap_in_html_document(
            body,
            title=f'{self._name} 预览',
            extra_head=f'<style>{inline_css}</style>',
        )

    def validate(self, transformed_content: str, metadata: Optional[dict] = None) -> list[dict]:
        warnings = []
        metadata = metadata or {}

        max_title = self._limits.get('max_title_length', 0)
        title = metadata.get('title', '')
        if max_title and len(title) > max_title:
            warnings.append({
                'level': 'error',
                'message': f'标题 {len(title)} 字超过平台限制 {max_title} 字',
                'field': 'title',
            })

        max_body = self._limits.get('max_body_length', 0)
        if max_body and len(transformed_content) > max_body:
            warnings.append({
                'level': 'warning',
                'message': f'正文超过 {max_body} 字限制',
                'field': 'body',
            })

        return warnings

    def simulate_publish(self, transformed_content: str, metadata: Optional[dict] = None) -> dict:
        metadata = metadata or {}
        title = metadata.get('title', '未命名')
        return self._make_simulated_result(
            success=True,
            message=f'模拟发布成功："{title[:20]}" 已发布到 {self._name}',
            extra={
                'content_to_copy': transformed_content,
                'platform_tip': f'内容已按 {self._name} 格式转换，请复制后手动发布',
            },
        )


# =============================================================================
# CustomContentRenderer — controlled by config
# =============================================================================

from app.transformers.base_renderer import BaseRenderer  # noqa: E402


class CustomContentRenderer(BaseRenderer):
    """A configurable renderer that follows rules from the platform config.

    Supports:
    - Prepend/append static text
    - Heading rewrite rules (prefix, max depth)
    - Emoji injection
    - Tag extraction and appending
    - Custom format transformation
    """

    def __init__(self, config: dict) -> None:
        self._config = config
        self._pre = config.get('preprocessor', {})

    def render(self, ast: ContentAST, metadata: Optional[dict] = None) -> str:
        metadata = metadata or {}
        parts: list[str] = []

        # Header template
        header = self._config.get('header_template', '')
        if header:
            parts.append(header.format(
                title=ast.title or metadata.get('title', ''),
            ))

        # Render content based on format mode
        mode = self._config.get('format', 'html')

        if mode == 'markdown' or mode == 'plain_text':
            parts.append(ast.get_text_content())
        elif mode == 'html':
            parts.append(self._render_as_html(ast))
        elif mode == 'json':
            import json
            parts.append(json.dumps({
                'title': ast.title,
                'content': ast.get_text_content(),
                'images': ast.images,
            }, ensure_ascii=False, indent=2))
        else:
            parts.append(ast.get_text_content())

        # Footer template
        footer = self._config.get('footer_template', '')
        if footer:
            parts.append(footer)

        result = '\n\n'.join(parts)

        # Apply preprocessor rules
        rules = self._pre
        if rules.get('max_heading_depth'):
            # Simple heading depth limiting
            import re
            depth = rules['max_heading_depth']
            result = re.sub(
                r'^#{' + str(depth + 1) + r',} ',
                '#' * depth + ' ',
                result,
                flags=re.MULTILINE,
            )

        if rules.get('add_tags') and metadata.get('tags'):
            tags = ' '.join(f'#{t}' for t in metadata.get('tags', []))
            result += f'\n\n{tags}'

        if rules.get('emoji_prefix'):
            result = rules['emoji_prefix'] + '\n' + result

        return result

    def _render_as_html(self, ast: ContentAST) -> str:
        """Render to HTML using the base renderer's methods."""
        from app.transformers.renderers.bilibili_renderer import BilibiliRenderer
        return BilibiliRenderer().render(ast)
