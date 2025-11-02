import pytest
from httpx import AsyncClient, ASGITransport
from api.main import app


@pytest.mark.unit
@pytest.mark.asyncio
async def test_list_simulations_history_empty():
    """Проверяем, что при отсутствии симуляций возвращается пустой список"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/simulations_history/")

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_simulation_not_found():
    """Проверяем, что при запросе несуществующей симуляции возвращается 404"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/simulations_history/9999")

    assert response.status_code == 404
    assert "Simulation not found" in response.text
