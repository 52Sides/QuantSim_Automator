import pytest
import httpx
import os

BACKEND_URL = os.getenv("BACKEND_URL", "http://quantsim-backend:8000")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_simulations_history_flow():
    async with httpx.AsyncClient(base_url=BACKEND_URL) as client:
        payload = {"command": "TSLA-L-50% NVDA-L-50% 2020-01-01 2020-12-31"}
        resp = await client.post("/simulate/", json=payload)
        assert resp.status_code == 200

        list_resp = await client.get("/simulations_history/")
        assert list_resp.status_code == 200
        data = list_resp.json()
        assert isinstance(data, list)
        assert len(data) >= 1

        sim_id = data[0]["id"]
        detail_resp = await client.get(f"/simulations_history/{sim_id}")
        assert detail_resp.status_code == 200
        detail = detail_resp.json()
        assert "metrics" in detail
        assert "portfolio" in detail
