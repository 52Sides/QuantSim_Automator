import os
import pytest
import pytest_asyncio
import socket
import warnings
import inspect
from pathlib import Path

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from httpx import AsyncClient
import asyncio

from db.database import Base, get_db
from api.main import app
import api.routers.simulate as simulate_router
import api.routers.simulations_history as history_router
from alembic.config import Config
from db.models import SimulationModel


def pytest_configure():
    warnings.filterwarnings("ignore", category=ResourceWarning)


@pytest.fixture(scope="function")
async def async_client():
    """
    Фикстура для реальных integration-тестов.
    Поднимает httpx.AsyncClient, который шлёт запросы прямо в запущенное FastAPI-приложение.
    """
    async with AsyncClient(base_url="http://backend:8000") as client:
        yield client


@pytest_asyncio.fixture(scope="function")
async def db_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture(autouse=False)
def skip_if_no_postgres():
    """
    Пропускает тесты, если Postgres не доступен внутри контейнера.
    """
    db_host = os.getenv("POSTGRES_HOST", "postgres")
    db_port = int(os.getenv("POSTGRES_PORT", 5432))

    try:
        socket.create_connection((db_host, db_port), timeout=1).close()
    except OSError:
        pytest.skip(f"Пропуск: PostgreSQL {db_host}:{db_port} недоступен")


@pytest.fixture(autouse=True)
def override_db_for_unit_tests(request):
    if "unit" in request.keywords:
        class DummyResult:
            def scalar_one_or_none(self):
                return None

            def scalars(self):
                class S:
                    def unique(self):
                        return self

                    def all(self):
                        return []

                return S()

        class DummySession:
            async def execute(self, *a, **kw):
                return DummyResult()

            async def commit(self):
                pass

            async def flush(self):
                pass

            async def rollback(self):
                pass

            def add(self, *a, **kw):
                pass

        async def fake_get_db():
            yield DummySession()

        # Подменяем не только в app, но и во всех зарегистрированных модулях
        app.dependency_overrides[get_db] = fake_get_db
        for module in (simulate_router, history_router):
            for name, obj in inspect.getmembers(module):
                if name == "get_db":
                    setattr(module, name, fake_get_db)

        yield
        app.dependency_overrides.clear()
    else:
        yield


@pytest.fixture(scope="session")
def alembic_config():
    """
    Возвращает Alembic Config с корректным script_location.
    Работает внутри backend контейнера.
    """
    # Абсолютный путь до alembic.ini внутри контейнера
    alembic_ini_path = Path("/app/src/db/migrations/alembic.ini")
    if not alembic_ini_path.exists():
        raise FileNotFoundError(f"Alembic ini not found at {alembic_ini_path}")

    config = Config(str(alembic_ini_path))
    return config


import pytest
from services.worker.celery_app import celery_app


@pytest.fixture(scope="session")
def celery_enable_logging():
    """Включаем логирование Celery при интеграционных тестах."""
    return True


@pytest.fixture(scope="session")
def celery_config():
    """Конфигурация Celery для тестового окружения."""
    return {
        "broker_url": "redis://redis:6379/0",
        "result_backend": "redis://redis:6379/0",
        "task_always_eager": False,  # Важно: пусть реально идёт через брокер
        "task_default_queue": "default",
        "worker_send_task_events": True,
    }


@pytest.fixture(scope="session")
def celery_includes():
    """Указываем Celery, какие таски подхватывать при тестах."""
    return ["services.worker.tasks"]


@pytest.fixture(scope="session")
def celery_app(celery_app):
    """
    Подключает реальный celery_app, который уже определён в нашем проекте.
    Используется pytest-celery для инициализации воркера.
    """
    return celery_app

# --- AUTH TEST FIXTURES ---

@pytest_asyncio.fixture(scope="function")
async def async_test_db():
    """
    Отдельная БД для unit/integration-тестов (SQLite in-memory).
    Сбрасывает все таблицы перед каждым тестом.
    """
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async def _get_test_db():
        async with async_session() as session:
            yield session

    # Подменяем зависимость get_db → тестовую
    app.dependency_overrides[get_db] = _get_test_db

    yield async_session

    app.dependency_overrides.clear()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def test_client(async_test_db):
    """
    Клиент для запросов в тестовом приложении.
    Работает с in-memory базой.
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
def mock_simulation_in_db(db_session):
    sim = SimulationModel(
        command="TSLA-L-50% AAPL-S-50%",
        metrics={"cagr": 0.12, "sharpe": 1.4, "max_drawdown": 0.15},
        portfolio=[{"date": "2021-01-01", "portfolio_value": 10000}]
    )
    db_session.add(sim)
    db_session.commit()
    return sim
