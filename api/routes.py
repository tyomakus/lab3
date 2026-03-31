# api/routes.py
from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from datetime import datetime

from database.sql_db import get_sql_db
from database.mongo_db import comments_col, statistics_col
from database.redis_db import get_redis
from database.models import Article
from schemas.schemas import ArticleCreate, CommentCreate
from utils import get_cached_rating, update_statistics
from database.models import Author
from database.crud import (
    get_authors, get_categories, get_issues,
    get_authors_with_article_count,
    get_categories_with_stats,
    get_issues_with_stats
)





router = APIRouter()
templates = Jinja2Templates(directory="templates")

# --- Авторы ---
@router.get("/authors")
async def authors_page(request: Request, db: AsyncSession = Depends(get_sql_db)):
    result = await db.execute(select(Author))
    authors = result.scalars().all()
    return templates.TemplateResponse(
        request=request, 
        name="authors.html", 
        context={"authors": authors}
    )

@router.post("/authors/new")
async def create_author_page(name: str = Form(...), email: str = Form(...), db: AsyncSession = Depends(get_sql_db)):
    new_author = Author(name=name, email=email)
    db.add(new_author)
    await db.commit()
    return RedirectResponse("/authors", status_code=303)


# Главная — список всех статей
@router.get("/")
async def index(request: Request, db: AsyncSession = Depends(get_sql_db)):
    result = await db.execute(select(Article))
    articles = result.scalars().all()
    return templates.TemplateResponse(
        request=request, name="index.html", context={"articles": articles}
    )


# Страница добавления статьи с выбором из списков
@router.get("/articles/new")
async def add_article_page(request: Request, db: AsyncSession = Depends(get_sql_db)):
    authors = await get_authors(db)
    categories = await get_categories(db)
    issues = await get_issues(db)
    return templates.TemplateResponse(
        request=request,
        name="add_article.html",
        context={
            "authors": authors,
            "categories": categories,
            "issues": issues
        }
    )


# Создание новой статьи
@router.post("/articles/new")
async def create_article(
    title: str = Form(...),
    content: str = Form(...),
    author_id: int = Form(...),
    category_id: int = Form(...),
    issue_id: int = Form(...),
    db: AsyncSession = Depends(get_sql_db)
):
    article_data = ArticleCreate(
        title=title,
        content=content,
        author_id=author_id,
        category_id=category_id,
        issue_id=issue_id
    )
    new_article = Article(**article_data.model_dump())
    db.add(new_article)
    await db.commit()
    return RedirectResponse(url="/", status_code=303)





# Добавление комментария
@router.post("/articles/{article_id}/comments")
async def add_comment(
    article_id: int,
    author: str = Form("Аноним"),
    text: str = Form(...),
    rating: int = Form(...),
    rd=Depends(get_redis)
):
    comment_data = CommentCreate(
        article_id=article_id,
        author=author,
        text=text,
        rating=rating
    )
    await comments_col.insert_one(comment_data.model_dump())

    # Увеличить общий счетчик комментариев в Redis
    await rd.incr("total:comments")

    # удалить старый кеш среднего рейтинга
    await rd.delete(f"article:{article_id}:avg_rating")

    return RedirectResponse(url=f"/articles/{article_id}", status_code=303)


# Поиск статей по названию или содержимому
@router.get("/search")
async def search(
    request: Request,
    q: str = None,
    min_rating: int = 0,
    db: AsyncSession = Depends(get_sql_db),
    rd=Depends(get_redis)
):
    is_search_triggered = "q" in request.query_params
    if is_search_triggered and (not q or not q.strip()):
        return templates.TemplateResponse(request=request, name="search.html", context={"error": "Введите запрос!"})
    if not is_search_triggered:
        return templates.TemplateResponse(request=request, name="search.html", context={})

    stmt = select(Article).where(
        or_(Article.title.ilike(f"%{q}%"), Article.content.ilike(f"%{q}%"))
    )
    result = await db.execute(stmt)
    articles = result.scalars().all()

    final_results = []
    for article in articles:
        avg = await get_cached_rating(article.id, rd)
        if avg >= min_rating:
            final_results.append({
                "article": article,
                "avg_rating": round(avg, 1) if avg > 0 else "Нет"
            })

    return templates.TemplateResponse(
        request=request,
        name="search.html",
        context={"results": final_results, "q": q}
    )


# Популярные статьи
@router.get("/popular")
async def popular_articles(
    request: Request,
    db: AsyncSession = Depends(get_sql_db),
    rd=Depends(get_redis)
):
    top_list = await rd.zrevrange("popular:articles", 0, 9, withscores=True)
    results = []
    for article_id_str, views in top_list:
        article = await db.get(Article, int(article_id_str))
        if article:
            results.append({"article": article, "views": int(views)})

    return templates.TemplateResponse(
        request=request,
        name="popular.html",
        context={"results": results}
    )
# Детали статьи + комментарии + рейтинг
@router.get("/articles/{article_id}")
async def article_detail(
    request: Request, article_id: int,
    db: AsyncSession = Depends(get_sql_db),
    rd=Depends(get_redis)
):
    article = await db.get(Article, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Статья не найдена")

    # увеличить популярность в Redis
    await rd.zincrby("popular:articles", 1, str(article_id))

    # Увеличить общий счетчик просмотров в Redis
    await rd.incr("total:views")

    # Получаем просмотры из Redis
    views_count = await rd.zscore("popular:articles", str(article_id))
    if views_count:
        views_count = int(views_count)
    else:
        views_count = 0

    # средний рейтинг с кеша
    avg_rating = await get_cached_rating(article_id, rd)

    # последние комментарии из MongoDB
    comments = await comments_col.find({"article_id": article_id}).sort("created_at", -1).to_list(100)

    print(f"DEBUG: views_count={views_count}, avg_rating={avg_rating}")  # Отладка

    return templates.TemplateResponse(
        request=request,
        name="article_detail.html",
        context={
            "article": article,
            "comments": comments,
            "avg_rating": round(avg_rating, 1) if avg_rating else None,
            "views_count": views_count,  # Добавляем просмотры
            "views": views_count  # Дублируем для проверки
        }
    )


# Статистика с использованием JOIN и GROUP BY
@router.get("/statistics")
async def statistics_page(
    request: Request,
    db: AsyncSession = Depends(get_sql_db),
    rd=Depends(get_redis)
):
    # Получаем статистику авторов с COUNT
    authors_stats = await get_authors_with_article_count(db)

    # Получаем статистику категорий
    categories_stats = await get_categories_with_stats(db)

    # Получаем статистику выпусков с COUNT и DISTINCt
    issues_stats = await get_issues_with_stats(db)

    # Получаем счетчики из Redis (новые просмотры и комментарии)
    total_views_redis = await rd.get("total:views")
    total_comments_redis = await rd.get("total:comments")

    # Получаем старую статистику из MongoDB
    mongo_stats = await statistics_col.find_one({"_id": "global"})
    old_views = mongo_stats.get("total_views", 0) if mongo_stats else 0
    old_comments = mongo_stats.get("total_comments", 0) if mongo_stats else 0

    # Объединяем старую статистику с новой
    mongo_stats = {
        "total_views": old_views + (int(total_views_redis) if total_views_redis else 0),
        "total_comments": old_comments + (int(total_comments_redis) if total_comments_redis else 0)
    }

    # Получаем список популярных статей из Redis
    top_articles = await rd.zrevrange("popular:articles", 0, 4, withscores=True)

    return templates.TemplateResponse(
        request=request,
        name="statistics.html",
        context={
            "authors_stats": authors_stats,
            "categories_stats": categories_stats,
            "issues_stats": issues_stats,
            "mongo_stats": mongo_stats,
            "top_articles": top_articles
        }
    )
