from __future__ import annotations

import os
from typing import AsyncGenerator

from core.config import settings
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, declared_attr
from sqlalchemy import MetaData


# --- Base ORM setup ---
class Base(DeclarativeBase):
    """Базовый класс для всех ORM моделей"""

    metadata = MetaData(schema=None)

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.replace("Model", "").lower() + "s"


engine = create_async_engine(settings.DATABASE_URL, echo=False, future=True)

AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


# --- Dependency for FastAPI ---
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency для получения асинхронной сессии SQLAlchemy в эндпоинтах FastAPI.
    """
    async with AsyncSessionLocal() as session:
        yield session


# --- Инициализация / очистка БД (утилиты) ---
async def init_db() -> None:
    """
    Создать все таблицы (используется в тестах или при первом запуске).
    Alembic миграции будут предпочтительнее в продакшене.
    """
    import backend.src.db.models as models  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_db() -> None:
    """Удалить все таблицы (используется в тестах)."""
    import backend.src.db.models as models  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
