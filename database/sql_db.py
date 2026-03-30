from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from config import settings

engine = create_async_engine(settings.DATABASE_SQL_URL)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def get_sql_db():
    async with AsyncSessionLocal() as session:
        yield session
