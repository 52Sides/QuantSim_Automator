import os
import pytest
import pytest_asyncio
import socket
import warnings
import inspect

from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from db.database import Base, get_db
from api.main import app
import api.routers.simulate as simulate_router
import api.routers.simulations_history as history_router


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


@pytest_asyncio.fixture(scope="function")
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture(autouse=False)
def skip_if_no_postgres():
    """Пропускает тест, если нет PostgreSQL (локально)."""
    db_url = os.getenv("DATABASE_URL", "")
    is_ci = os.getenv("CI", "").lower() == "true"

    if is_ci or "postgresql" in db_url:
        # проверим доступность порта для красоты
        host = "postgres" if "postgres" in db_url else "localhost"
        try:
            socket.create_connection((host, 5432), timeout=1).close()
            return
        except OSError:
            pass

    pytest.skip("Пропуск: PostgreSQL не запущен или не в CI окружении.")


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
