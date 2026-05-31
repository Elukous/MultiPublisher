"""Text processing utilities for content adaptation."""

from __future__ import annotations

import re


def truncate_text(text: str, max_length: int, suffix: str = '...') -> str:
    """Truncate text to max_length characters, appending suffix if truncated."""
    if len(text) <= max_length:
        return text
    # Try to break at a sentence or clause boundary
    truncated = text[:max_length - len(suffix)]
    # Find the last sentence-ending punctuation
    for sep in ['。', '！', '？', '.', '！', '？', '；', ';', '\n']:
        idx = truncated.rfind(sep)
        if idx > max_length // 2:
            return truncated[:idx + 1] + suffix
    return truncated + suffix


def extract_title(text: str, max_length: int = 50) -> str:
    """Extract a title from text content.

    Strategy:
    1. Use first line if it looks like a heading.
    2. Use first sentence.
    3. Truncate to max_length.
    """
    lines = text.strip().split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # Strip leading markdown heading markers
        clean = re.sub(r'^#+\s*', '', line)
        if clean:
            return clean[:max_length]
    return text[:max_length]


def count_words(text: str) -> int:
    """Count words in mixed Chinese/English text."""
    # Chinese characters
    chinese_chars = len(re.findall(r'[一-鿿]', text))
    # English words
    english_words = len(re.findall(r'[a-zA-Z]+', text))
    return chinese_chars + english_words


def count_chars(text: str) -> int:
    """Count visible characters (excluding whitespace)."""
    return len(re.sub(r'\s', '', text))


EMOJI_MAP = {
    'start': ['✨', '🔥', '💡', '📌', '🎯'],
    'highlight': ['⭐', '🌟', '❗', '💪', '👍'],
    'list_item': ['👉', '✅', '🔹', '▪️', '➡️'],
    'warning': ['⚠️', '🔔', '❗'],
    'end': ['💬', '🙏', '❤️', '🤝', '👏'],
}

# Common tags for different content types
TOPIC_EMOJIS = {
    '技术': '💻',
    '编程': '👨‍💻',
    'Python': '🐍',
    '效率': '⚡',
    '设计': '🎨',
    '美食': '🍜',
    '旅行': '✈️',
    '生活': '🏡',
    '学习': '📚',
    '职场': '💼',
    '摄影': '📷',
    '健身': '💪',
    '音乐': '🎵',
    '电影': '🎬',
    '读书': '📖',
}


def suggest_emojis(text: str, count: int = 3) -> list[str]:
    """Suggest relevant emojis based on content text."""
    suggestions = []
    for topic, emoji in TOPIC_EMOJIS.items():
        if topic in text and emoji not in suggestions:
            suggestions.append(emoji)
        if len(suggestions) >= count:
            break

    # Fill remaining with defaults
    defaults = EMOJI_MAP['start']
    for emoji in defaults:
        if emoji not in suggestions:
            suggestions.append(emoji)
        if len(suggestions) >= count:
            break

    return suggestions[:count]


def extract_tags(text: str, max_tags: int = 5) -> list[str]:
    """Extract potential hashtag topics from text.

    Uses heading text and high-frequency keywords as tag candidates.
    """
    tags: list[str] = []

    # Extract heading text
    headings = re.findall(r'^#+\s+(.+)$', text, re.MULTILINE)
    for h in headings:
        clean = h.strip()
        if clean and len(clean) <= 10:
            tags.append(f'#{clean}')
        if len(tags) >= max_tags:
            return tags

    # Look for capitalized English words as potential tags
    en_words = re.findall(r'\b[A-Z][a-zA-Z]+\b', text)
    seen = set()
    for w in en_words:
        if w not in seen and len(w) > 2:
            tags.append(f'#{w}')
            seen.add(w)
        if len(tags) >= max_tags:
            break

    return tags


def add_space_between_cn_en(text: str) -> str:
    """Add space between Chinese and English/number characters (Zhihu norm)."""
    # Between Chinese and English
    text = re.sub(r'([一-鿿])([a-zA-Z])', r'\1 \2', text)
    text = re.sub(r'([a-zA-Z])([一-鿿])', r'\1 \2', text)
    # Between Chinese and numbers
    text = re.sub(r'([一-鿿])(\d)', r'\1 \2', text)
    text = re.sub(r'(\d)([一-鿿])', r'\1 \2', text)
    return text
