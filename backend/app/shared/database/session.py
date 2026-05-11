"""Async SQLAlchemy engine + session factory."""
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.shared.contrib.config import settings

engine = create_async_engine(
    settings.database.dsn,
    pool_size=settings.database.pool_size,
    max_overflow=settings.database.max_overflow,
    echo=settings.database.echo,
    pool_pre_ping=True,
)

SessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False,
)


async def get_session() -> AsyncIterator[AsyncSession]:
    """FastAPI dependency. One session per request."""
    async with SessionLocal() as session:
        yield session


@asynccontextmanager
async def get_session_bg() -> AsyncIterator[AsyncSession]:
    """For background tasks / scheduler / scripts — used with `async with`."""
    async with SessionLocal() as session:
        yield session
