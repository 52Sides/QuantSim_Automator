from fastapi.testclient import TestClient
from api.main import app


def test_simulate_valid_command():
    """Проверяем, что корректная команда возвращает метрики"""
    # Используем контекстный менеджер для автоматического закрытия клиента
    with TestClient(app) as client:
        response = client.post("/simulate/", json={
            "command": "TSLA-L-50% AAPL-S-50% 2020-01-01 2021-01-01"
        })

        assert response.status_code == 200

        data = response.json()

        # Проверяем базовые ключи
        assert "cagr" in data
        assert "sharpe" in data
        assert "max_drawdown" in data
        assert "portfolio" in data
        assert isinstance(data["portfolio"], list)


def test_simulate_invalid_command():
    """Проверяем, что некорректная команда вызывает ошибку"""
    with TestClient(app) as client:
        response = client.post("/simulate/", json={
            "command": "INVALID INPUT"
        })
        assert response.status_code in (400, 422)
