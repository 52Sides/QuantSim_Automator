import asyncio
import pytest
from httpx import AsyncClient, ASGITransport
from api.main import app


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_simulate_async_full_flow():
    """
    Интеграционный тест полного цикла асинхронной симуляции через Celery + Redis.
    Проверяет: создание задачи, получение статуса, успешное завершение и структуру результата.
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. Отправляем запрос на создание асинхронной задачи
        response = await client.post(
            "/simulate/async",
            json={"command": "AAPL-L-100% 2020-01-01 2020-12-31"},
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert "task_id" in data
        task_id = data["task_id"]

        # 2. Ждём выполнения задачи
        for _ in range(10):
            await asyncio.sleep(2)
            status_resp = await client.get(f"/simulate/status/{task_id}")
            assert status_resp.status_code == 200, status_resp.text
            status_data = status_resp.json()
            if status_data["status"] == "SUCCESS":
                result = status_data.get("result")
                assert result, "Expected result in successful task response"
                assert "cagr" in result
                assert "sharpe" in result
                assert "max_drawdown" in result
                assert "portfolio" in result
                break
        else:
            pytest.fail("Task did not complete with SUCCESS status within timeout")
