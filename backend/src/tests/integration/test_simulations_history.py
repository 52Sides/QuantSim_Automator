import pytest
import httpx


@pytest.mark.integration
@pytest.mark.asyncio
async def test_simulations_history_flow():
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
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
