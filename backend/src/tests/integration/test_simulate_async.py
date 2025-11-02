import pytest
import asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import SimulationModel
from services.worker.tasks import run_simulation_task
import redis.asyncio as aioredis


@pytest.mark.integration
@pytest.mark.asyncio
async def test_simulate_async_starts_task(async_client: AsyncClient):
    payload = {"command": "AAPL-L-100% 2020-01-01 2020-12-31"}
    resp = await async_client.post("/simulate/async", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "task_id" in data
    assert data["status"] == "PENDING"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_task_status_running(monkeypatch, async_client: AsyncClient):
    # Подготовим фейковые данные в Redis
    redis = aioredis.from_url("redis://redis:6379", decode_responses=True)
    await redis.hset("simulation:test_task", mapping={"status": "running", "progress": 42})

    resp = await async_client.get("/simulate/status/test_task")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "running"
    assert data["progress"] == 42


@pytest.mark.integration
@pytest.mark.asyncio
async def test_worker_saves_result_to_db(db_session: AsyncSession):
    # Запускаем задачу напрямую, имитируя Celery
    result = run_simulation_task("AAPL-L-100% 2020-01-01 2020-12-31")
    assert result["status"] == "done"
    assert "portfolio" in result["result"]

    # Проверяем, что симуляция действительно появилась в БД
    res = await db_session.execute(SimulationModel.__table__.select())
    sim = res.scalar_one_or_none()
    assert sim is not None
    assert sim.command.startswith("AAPL")
