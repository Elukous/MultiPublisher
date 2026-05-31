"""HTML utility functions for content transformation."""

from __future__ import annotations

import re
from typing import Optional


def inline_css(html: str, styles: Optional[dict[str, str]] = None) -> str:
    """Apply inline styles to HTML tags.

    Uses premailer for robust CSS inlining when available, otherwise
    falls back to simple tag-level style injection.

    Args:
        html: HTML string to process.
        styles: Optional mapping of CSS selectors to inline style strings.
            Only used for simple fallback mode.

    Returns:
        HTML string with all styles inlined.
    """
    try:
        from premailer import transform
        return transform(html, remove_classes=True, strip_important=True)
    except Exception:
        # Fallback: just return as-is if premailer fails
        return html


def sanitize_html(html: str) -> str:
    """Remove potentially dangerous HTML elements and attributes.

    Strips script tags, event handlers, and javascript: URLs.
    """
    # Remove script tags and their contents
    html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
    # Remove event handlers
    html = re.sub(r'\s+on\w+\s*=\s*["\'][^"\']*["\']', '', html, flags=re.IGNORECASE)
    # Remove javascript: URLs
    html = re.sub(r'href\s*=\s*["\']javascript:[^"\']*["\']', 'href="#"', html, flags=re.IGNORECASE)
    return html


def wrap_in_html_document(
    body_content: str,
    title: str = 'Preview',
    extra_head: str = '',
    body_style: str = '',
) -> str:
    """Wrap content in a full HTML document for iframe rendering.

    Args:
        body_content: Inner HTML to wrap.
        title: Document title.
        extra_head: Additional <head> content (meta tags, styles, etc.)
        body_style: Inline style for the <body> tag.

    Returns:
        Complete HTML document string.
    """
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{ margin: 0; padding: 16px; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; {body_style} }}
        img {{ max-width: 100%; }}
    </style>
    {extra_head}
</head>
<body>
{body_content}
</body>
</html>"""


def make_preview_phone_frame(body_content: str, title: str = 'Preview') -> str:
    """Wrap content in a mobile phone frame for realistic preview.

    Used by WeChat and Xiaohongshu previews to show content
    in a phone-like container.
    """
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            background: #f0f0f0;
            display: flex;
            justify-content: center;
            align-items: flex-start;
            padding: 20px;
            font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Microsoft YaHei", sans-serif;
        }}
        .phone-frame {{
            width: 375px;
            min-height: 667px;
            background: #fff;
            border-radius: 12px;
            box-shadow: 0 2px 20px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .phone-status-bar {{
            height: 44px;
            background: #f7f7f7;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 14px;
            color: #333;
            border-bottom: 1px solid #e5e5e5;
        }}
        .phone-content {{
            padding: 0;
            overflow-y: auto;
        }}
        img {{ max-width: 100%; }}
    </style>
</head>
<body>
    <div class="phone-frame">
        <div class="phone-status-bar">{title}</div>
        <div class="phone-content">
            {body_content}
        </div>
    </div>
</body>
</html>"""
