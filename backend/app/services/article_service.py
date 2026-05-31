"""Article service: JSON file-based CRUD for articles (V1 storage)."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from app.config import settings
from app.utils.text_processing import count_words


class ArticleService:
    """Simple JSON file-based article storage.

    Articles are stored as individual JSON files in backend/data/articles/.
    Can be swapped to a database later by implementing the same interface.
    """

    def __init__(self, data_dir: Path | None = None) -> None:
        self._dir = data_dir or settings.data_dir / 'articles'
        self._dir.mkdir(parents=True, exist_ok=True)

    def _path(self, article_id: str) -> Path:
        return self._dir / f'{article_id}.json'

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def create(
        self,
        title: str,
        content: str,
        tags: Optional[list[str]] = None,
        cover_image: Optional[str] = None,
    ) -> dict:
        """Create a new article and return its data."""
        article_id = uuid.uuid4().hex[:12]
        now = self._now()
        article = {
            'id': article_id,
            'title': title,
            'content': content,
            'tags': tags or [],
            'cover_image': cover_image,
            'word_count': count_words(content),
            'created_at': now,
            'updated_at': now,
        }
        self._path(article_id).write_text(
            json.dumps(article, ensure_ascii=False, indent=2), encoding='utf-8'
        )
        return article

    def get(self, article_id: str) -> Optional[dict]:
        """Get an article by ID. Returns None if not found."""
        path = self._path(article_id)
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding='utf-8'))

    def update(
        self,
        article_id: str,
        title: Optional[str] = None,
        content: Optional[str] = None,
        tags: Optional[list[str]] = None,
        cover_image: Optional[str] = None,
    ) -> Optional[dict]:
        """Update an article. Returns updated data or None if not found."""
        article = self.get(article_id)
        if article is None:
            return None

        if title is not None:
            article['title'] = title
        if content is not None:
            article['content'] = content
            article['word_count'] = count_words(content)
        if tags is not None:
            article['tags'] = tags
        if cover_image is not None:
            article['cover_image'] = cover_image

        article['updated_at'] = self._now()
        self._path(article_id).write_text(
            json.dumps(article, ensure_ascii=False, indent=2), encoding='utf-8'
        )
        return article

    def delete(self, article_id: str) -> bool:
        """Delete an article. Returns True if deleted, False if not found."""
        path = self._path(article_id)
        if path.exists():
            path.unlink()
            return True
        return False

    def list_all(self) -> list[dict]:
        """List all articles, sorted by updated_at descending."""
        articles = []
        for path in self._dir.glob('*.json'):
            try:
                data = json.loads(path.read_text(encoding='utf-8'))
                articles.append({
                    'id': data['id'],
                    'title': data['title'],
                    'tags': data.get('tags', []),
                    'word_count': data.get('word_count', 0),
                    'created_at': data.get('created_at', ''),
                    'updated_at': data.get('updated_at', ''),
                })
            except (json.JSONDecodeError, KeyError):
                continue
        articles.sort(key=lambda a: a.get('updated_at', ''), reverse=True)
        return articles
