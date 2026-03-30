from fastapi import FastAPI
from api.routes import router
from database.sql_db import engine
from database.models import Base

app = FastAPI(title="Car Shop Hybrid")

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app.include_router(router)
