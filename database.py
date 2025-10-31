import os
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import text

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@db:5432/eyemap")

import os
print("DATABASE_URL =", os.getenv("DATABASE_URL"))

engine = create_async_engine(DATABASE_URL, echo=False, future=True)
AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session

async def init_db():
    # create tables and enable postgis extension if possible
    async with engine.begin() as conn:
        # enable PostGIS (will fail harmlessly on SQLite or other DBs)
        try:
            await conn.execute(text('CREATE EXTENSION IF NOT EXISTS postgis;'))
        except Exception:
            pass
        from app import models
        await conn.run_sync(models.Base.metadata.create_all)
