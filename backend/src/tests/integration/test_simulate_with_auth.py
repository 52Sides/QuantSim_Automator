import pytest


@pytest.mark.integration
@pytest.mark.asyncio
async def test_simulate_with_auth(async_client):
    """Проверяет, что авторизованный пользователь может запустить симуляцию"""

    # --- 1. Регистрируем нового пользователя ---
    email = "sim_user@test.com"
    password = "pass123"
    resp = await async_client.post("/auth/register", json={"email": email, "password": password})
    assert resp.status_code in (200, 201), f"Register failed: {resp.text}"

    # --- 2. Логинимся и получаем токен ---
    resp = await async_client.post("/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200, f"Login failed: {resp.text}"
    body = resp.json()
    token = body["access_token"]

    # --- 3. Отправляем запрос /simulate с токеном ---
    command = "AAPL:0.5 MSFT:0.5 2023-01-01 2023-06-01"
    resp = await async_client.post(
        "/simulate/",
        headers={"Authorization": f"Bearer {token}"},
        json={"command": command}
    )
    assert resp.status_code == 200, f"Simulate failed: {resp.text}"

    data = resp.json()
    assert "cagr" in data
    assert "sharpe" in data
    assert "portfolio" in data
    assert isinstance(data["portfolio"], list)
