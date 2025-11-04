import pytest


@pytest.mark.integration
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


@pytest.mark.integration
@pytest.mark.asyncio
async def test_auth_flow(test_client):
    # ---------- Register ----------
    r = await test_client.post("/auth/register", json={
        "email": "demo@example.com",
        "password": "password123"
    })
    assert r.status_code == 201
    data = r.json()
    assert "id" in data

    # ---------- Login ----------
    r = await test_client.post("/auth/login", json={
        "email": "demo@example.com",
        "password": "password123"
    })
    assert r.status_code == 200
    tokens = r.json()
    access = tokens["access_token"]
    refresh = tokens["refresh_token"]

    assert access and refresh

    # ---------- Refresh ----------
    r = await test_client.post("/auth/refresh", params={"refresh_token": refresh})
    assert r.status_code == 200
    refreshed = r.json()
    assert "access_token" in refreshed
    assert refreshed["access_token"] != access

    # ---------- Logout ----------
    r = await test_client.post("/auth/logout", params={"refresh_token": refresh})
    assert r.status_code == 200
    assert r.json()["detail"] == "Logged out"

    # ---------- Refresh after logout (should fail) ----------
    r = await test_client.post("/auth/refresh", params={"refresh_token": refresh})
    assert r.status_code == 401
