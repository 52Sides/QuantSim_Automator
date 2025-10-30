import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


def test_simulate_router_success(monkeypatch):
    """Проверяем успешный сценарий симуляции"""

    # Мокаем зависимые функции (чтобы не тянуть реальный yfinance)
    import core

    def fake_parse(cmd):
        return {"AAPL": 1.0}, {"AAPL": "L"}, "2020-01-01", "2020-06-01"

    def fake_build(weights, sides, start, end, budget):
        import pandas as pd
        idx = pd.date_range(start, end, freq="ME")
        return pd.Series([100 + i for i in range(len(idx))], index=idx)

    class FakeSimulator:
        def __init__(self, series): ...

        def run(self):
            import pandas as pd
            idx = pd.date_range("2020-01-01", "2020-06-01", freq="ME")
            returns = pd.Series([0.01] * (len(idx) - 1), index=idx[1:])
            cumulative = pd.Series([1.0 + i * 0.01 for i in range(len(idx))], index=idx)
            return core.SimulationResult(
                returns=returns,
                cumulative=cumulative,
                cagr=0.1, sharpe=1.2, max_drawdown=0.05, meta={}
            )

    monkeypatch.setattr("api.routers.simulate.parse_command_safe", fake_parse)
    monkeypatch.setattr("api.routers.simulate.build_portfolio_series", fake_build)
    monkeypatch.setattr("api.routers.simulate.PortfolioSimulator", FakeSimulator)

    response = client.post("/simulate/", json={"command": "FAKE-L-100% 2020-01-01 2020-06-01"})
    assert response.status_code == 200

    data = response.json()
    assert set(data.keys()) == {"cagr", "sharpe", "max_drawdown", "portfolio"}
    assert isinstance(data["portfolio"], list)
    assert data["cagr"] == 0.1


def test_simulate_router_failure(monkeypatch):
    """Проверяем обработку ошибки"""
    import core

    def bad_parse(_):
        raise ValueError("Invalid input")

    monkeypatch.setattr(core, "parse_command_safe", bad_parse)

    response = client.post("/simulate/", json={"command": "BAD INPUT"})
    assert response.status_code == 400
    assert "Invalid format" in response.text or "Invalid input" in response.text

