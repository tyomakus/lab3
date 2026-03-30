from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# --- Статьи ---
class ArticleBase(BaseModel):
    title: str = Field(..., max_length=200)
    content: str

class ArticleCreate(ArticleBase):
    author_id: int
    category_id: int
    issue_id: int

class ArticleRead(ArticleBase):
    id: int
    author_id: int
    category_id: int
    issue_id: int
    created_at: Optional[datetime]

    class Config:
        orm_mode = True

# --- Комментарии ---
class CommentBase(BaseModel):
    article_id: int
    author: str = "Аноним"
    text: str
    rating: int = Field(..., ge=1, le=5)

class CommentCreate(CommentBase):
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CommentRead(CommentBase):
    id: str = Field(alias="_id")
    created_at: datetime

    class Config:
        allow_population_by_field_name = True