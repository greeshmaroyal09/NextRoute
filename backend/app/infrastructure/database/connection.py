from __future__ import annotations
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.config import get_settings
from app.infrastructure.database.models import Base

settings = get_settings()

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True
)

async_sessionmaker_instance = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_sessionmaker_instance() as session:
        yield session

async def create_tables() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
