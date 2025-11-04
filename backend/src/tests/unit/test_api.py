import pytest
from httpx import AsyncClient, ASGITransport
from api.main import app


@pytest.mark.unit
@pytest.mark.asyncio
async def test_simulate_valid_command():
    """Проверяем, что корректная команда возвращает метрики"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/simulate/", json={"command": "TSLA-L-50% AAPL-S-50% 2020-01-01 2021-01-01"})

    assert response.status_code == 200
    data = response.json()
    assert "cagr" in data
    assert "sharpe" in data
    assert "max_drawdown" in data
    assert "portfolio" in data
    assert isinstance(data["portfolio"], list)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_simulate_invalid_command():
    """Проверяем, что некорректная команда вызывает ошибку"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/simulate/", json={"command": "INVALID INPUT"})

    # FastAPI может вернуть 400 (HTTPException) или 422 (валидация Pydantic)
    assert response.status_code in (400, 422)
