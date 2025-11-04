import pytest


@pytest.mark.unit
@pytest.mark.asyncio
async def test_register_and_login(async_client):
    # register
    resp = await async_client.post("/auth/register", json={"email": "t@test.com", "password": "pass123"})
    assert resp.status_code == 201

    # login
    resp = await async_client.post("/auth/login", json={"email": "t@test.com", "password": "pass123"})
    assert resp.status_code == 200
    body = resp.json()
    assert "access_token" in body and "refresh_token" in body
