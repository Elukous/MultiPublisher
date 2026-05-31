"""Article request/response schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ArticleCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    tags: list[str] = Field(default_factory=list)
    cover_image: Optional[str] = None


class ArticleUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[list[str]] = None
    cover_image: Optional[str] = None


class ArticleResponse(BaseModel):
    id: str
    title: str
    content: str
    tags: list[str]
    cover_image: Optional[str]
    word_count: int
    created_at: str
    updated_at: str


class ArticleListItem(BaseModel):
    id: str
    title: str
    tags: list[str]
    word_count: int
    created_at: str
    updated_at: str
