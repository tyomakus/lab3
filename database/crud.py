from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.models import Author, Category, Issue

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