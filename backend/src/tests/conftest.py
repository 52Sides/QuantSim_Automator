import os
import pytest
import pytest_asyncio
import socket
import warnings
import inspect
from pathlib import Path

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from db.database import Base, get_db
from api.main import app
import api.routers.simulate as simulate_router
import api.routers.simulations_history as history_router
from alembic.config import Config
import os
import pytest
from httpx import AsyncClient


def pytest_configure():
    warnings.filterwarnings("ignore", category=ResourceWarning)


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
