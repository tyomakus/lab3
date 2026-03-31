from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, join, desc
from database.models import Author, Category, Issue, Article

# --- Авторы ---
async def get_authors(db: AsyncSession):
    result = await db.execute(select(Author))
    return result.scalars().all()

async def create_author(db: AsyncSession, name: str, email: str):
    author = Author(name=name, email=email)
    db.add(author)
    await db.commit()
    await db.refresh(author)
    return author

# --- Категории ---
async def get_categories(db: AsyncSession):
    result = await db.execute(select(Category))
    return result.scalars().all()

# --- Выпуски ---
async def get_issues(db: AsyncSession):
    result = await db.execute(select(Issue))
    return result.scalars().all()

# --- ЗАПРОСЫ С JOIN И GROUP BY ---

# Количество статей по авторам (JOIN + COUNT)
async def get_authors_with_article_count(db: AsyncSession):
    stmt = select(
        Author.id,
        Author.name,
        Author.email,
        func.count(Article.id).label('article_count')
    ).select_from(Author).outerjoin(
        Article, Author.id == Article.author_id
    ).group_by(Author.id, Author.name, Author.email)

    result = await db.execute(stmt)
    return result.all()

# Статистика по категориям (JOIN + GROUP BY)
async def get_categories_with_stats(db: AsyncSession):
    stmt = select(
        Category.id,
        Category.title,
        func.count(Article.id).label('article_count')
    ).select_from(Category).outerjoin(
        Article, Category.id == Article.category_id
    ).group_by(Category.id, Category.title)

    result = await db.execute(stmt)
    return result.all()

# Статистика по выпускам (многоуровневый JOIN)
async def get_issues_with_stats(db: AsyncSession):
    stmt = select(
        Issue.id,
        Issue.number,
        Issue.publish_date,
        func.count(Article.id).label('article_count'),
        func.count(func.distinct(Author.id)).label('unique_authors')
    ).select_from(Issue).outerjoin(
        Article, Issue.id == Article.issue_id
    ).outerjoin(
        Author, Article.author_id == Author.id
    ).group_by(
        Issue.id, Issue.number, Issue.publish_date
    ).order_by(desc(Issue.publish_date))

    result = await db.execute(stmt)
    return result.all()
