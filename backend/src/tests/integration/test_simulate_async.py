import asyncio
import pytest
from httpx import AsyncClient, ASGITransport
from api.main import app


@pytest.mark.integration
@pytest.mark.asyncio
async def test_simulate_async_and_status():
    """Проверяет создание и статус асинхронной симуляции через Celery."""

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1️⃣ Запускаем задачу
        response = await client.post(
            "/simulate/async",
            json={"command": "AAPL-L-100% 2020-01-01 2020-12-31"},
        )

        assert response.status_code == 200, response.text
        data = response.json()
        assert "task_id" in data
        task_id = data["task_id"]

        # 2️⃣ Проверяем статус
        await asyncio.sleep(1)
        status_resp = await client.get(f"/simulate/status/{task_id}")
        assert status_resp.status_code == 200, status_resp.text

        status_data = status_resp.json()
        assert status_data["task_id"] == task_id
        assert status_data["status"] in ("PENDING", "SUCCESS", "FAILURE")

        # 3️⃣ Если задача готова — проверяем структуру результата
        if "result" in status_data and status_data["result"]:
            result = status_data["result"]
            assert "cagr" in result
            assert "portfolio" in result
