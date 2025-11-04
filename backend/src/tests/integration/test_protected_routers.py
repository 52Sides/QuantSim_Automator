import pytest

@pytest.mark.asyncio
async def test_simulate_requires_auth(async_client):
    resp = await async_client.post("/simulate", json={"command": "TSLA-L-100% AAPL-S-0% 2020-01-01 2021-01-01"})
    assert resp.status_code == 401

@pytest.mark.asyncio
async def test_simulate_with_auth(async_client):
    # регистрируем пользователя
    await async_client.post("/auth/register", json={"email": "u@test.com", "password": "pass123"})
    login = await async_client.post("/auth/login", json={"email": "u@test.com", "password": "pass123"})
    token = login.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    resp = await async_client.post(
        "/simulate",
        json={"command": "TSLA-L-100% AAPL-S-0% 2020-01-01 2021-01-01"},
        headers=headers,
    )
    assert resp.status_code in (200, 202)
    body = resp.json()
    assert "simulation_id" in body
