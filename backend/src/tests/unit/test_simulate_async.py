import pytest
from httpx import AsyncClient, ASGITransport
from api.main import app

@pytest.mark.unit
@pytest.mark.asyncio
async def test_async_simulation_start(monkeypatch):
    """Проверяем, что /simulate/async возвращает task_id"""
    class FakeTask:
        id = "12345"
        status = "PENDING"
    def fake_delay(cmd):
        return FakeTask()

    monkeypatch.setattr("services.worker.tasks.run_simulation_task.delay", fake_delay)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/simulate/async", json={"command": "AAPL-L-100% 2020-01-01 2021-01-01"})

    assert response.status_code == 200
    data = response.json()
    assert "task_id" in data
    assert data["status"] == "PENDING"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_status_success(monkeypatch):
    """Проверяем успешный ответ при готовой задаче"""
    class FakeResult:
        status = "SUCCESS"
        result = {"cagr": 0.1}

        def ready(self):
            return True

    def fake_result(task_id, app):
        return FakeResult()

    monkeypatch.setattr("api.routers.simulate_async.AsyncResult", fake_result)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/simulate/status/12345")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "SUCCESS"
    assert "result" in data
