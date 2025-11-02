import pytest
from httpx import AsyncClient, ASGITransport

from api.main import app
from core import SimulationResult


@pytest.mark.unit
@pytest.mark.asyncio
async def test_simulate_router_success(monkeypatch):
    """Проверяем успешный сценарий симуляции без реальных данных и БД."""

    import pandas as pd
    import api.routers.simulate as simulate

    # --- мок парсера ---
    def fake_parse(cmd):
        return {"AAPL": 1.0}, {"AAPL": "L"}, "2020-01-01", "2020-06-01"

    # --- мок билдера ---
    def fake_build(weights, sides, start, end, budget):
        idx = pd.date_range(start, end, freq="ME")
        return pd.Series([100 + i for i in range(len(idx))], index=idx)

    # --- мок симулятора ---
    class FakeSimulator:

        def __init__(self, series):
            pass

        def run(self):
            idx = pd.date_range("2020-01-01", "2020-06-01", freq="ME")
            cumulative = pd.Series([1.0 + i * 0.01 for i in range(len(idx))], index=idx)
            returns = cumulative.pct_change().fillna(0)
            return SimulationResult(
                returns=returns,
                cumulative=cumulative,
                cagr=0.1,
                sharpe=1.2,
                max_drawdown=0.05,
                meta={}
            )

    # --- применяем моки ---
    monkeypatch.setattr(simulate, "parse_command_safe", fake_parse)
    monkeypatch.setattr(simulate, "build_portfolio_series", fake_build)
    monkeypatch.setattr(simulate, "PortfolioSimulator", FakeSimulator)

    # --- импорт app после патчинга ---
    from api.main import app

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/simulate/", json={"command": "FAKE-L-100% 2020-01-01 2020-06-01"})

    assert response.status_code == 200
    data = response.json()
    assert set(data.keys()) == {"cagr", "sharpe", "max_drawdown", "portfolio"}
    assert isinstance(data["portfolio"], list)
    assert data["cagr"] == 0.1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_simulate_unexpected_error(monkeypatch):
    import api.routers.simulate as simulate

    def broken_parse(_):
        raise RuntimeError("Boom")

    monkeypatch.setattr(simulate, "parse_command_safe", broken_parse)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/simulate/", json={"command": "ANY"})
        assert resp.status_code == 400
        assert "Boom" in resp.text
