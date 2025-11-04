import pytest

@pytest.mark.asyncio
async def test_protected_endpoint_requires_token(async_client):
    # no token
    resp = await async_client.post("/simulate", json={"command": "TSLA-L-100% 2020-01-01 2020-12-31"})
    assert resp.status_code in (401, 403)

@pytest.mark.asyncio
async def test_protected_with_token(async_client):
    await async_client.post("/auth/register", json={"email": "p@test.com", "password": "pass123"})
    login = await async_client.post("/auth/login", json={"email": "p@test.com", "password": "pass123"})
    tokens = login.json()
    access = tokens["access_token"]
    headers = {"Authorization": f"Bearer {access}"}
    resp = await async_client.post("/simulate", json={"command": "TSLA-L-100% 2020-01-01 2020-12-31"}, headers=headers)
    assert resp.status_code in (200, 202)  # depending on sync/async simulate behavior
