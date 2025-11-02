import pytest
import httpx
import os

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_simulate_saves_to_db():
    async with httpx.AsyncClient(base_url=BACKEND_URL) as client:
        payload = {"command": "AAPL-L-100% 2020-01-01 2020-12-31"}
        response = await client.post("/simulate/", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "cagr" in data
        assert "portfolio" in data
