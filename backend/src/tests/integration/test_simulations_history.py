import pytest


@pytest.mark.integration
@pytest.mark.asyncio
async def test_simulations_history_flow(async_client):
    # Создаём симуляцию
    payload = {"command": "TSLA-L-50% NVDA-L-50% 2020-01-01 2020-12-31"}
    resp = await async_client.post("/simulate/", json=payload)
    assert resp.status_code == 200

    # Получаем список
    list_resp = await async_client.get("/simulations_history/")
    assert list_resp.status_code == 200
    data = list_resp.json()
    assert isinstance(data, list)
    assert len(data) >= 1

    # Получаем деталь
    sim_id = data[0]["id"]
    detail_resp = await async_client.get(f"/simulations_history/{sim_id}")
    assert detail_resp.status_code == 200
    detail = detail_resp.json()
    assert "metrics" in detail
    assert "portfolio" in detail
