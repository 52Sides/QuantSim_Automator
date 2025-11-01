import pytest
from httpx import AsyncClient


@pytest.mark.integration
@pytest.mark.asyncio
async def test_simulate_saves_to_db(async_client: AsyncClient, skip_if_no_postgres):
    payload = {"command": "AAPL-L-100% 2020-01-01 2020-12-31"}
    response = await async_client.post("/simulate/", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert "cagr" in data
    assert "portfolio" in data
