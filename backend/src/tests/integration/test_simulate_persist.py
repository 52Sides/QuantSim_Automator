import pytest
import httpx


@pytest.mark.integration
@pytest.mark.asyncio
async def test_simulate_saves_to_db(skip_if_no_postgres):
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        payload = {"command": "AAPL-L-100% 2020-01-01 2020-12-31"}
        response = await client.post("/simulate/", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert "cagr" in data
    assert "portfolio" in data
