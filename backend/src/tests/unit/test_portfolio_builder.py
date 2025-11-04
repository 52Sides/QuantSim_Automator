import pandas as pd
import pytest

from core.portfolio_builder import build_portfolio_series


def fake_fetch_price_series(ticker, start, end):
    """Возвращает искусственный временной ряд для тестов."""
    idx = pd.date_range(start, end)
    prices = pd.Series([100 + i for i in range(len(idx))], index=idx)
    return prices


@pytest.fixture(autouse=True)
def patch_fetcher(monkeypatch):
    monkeypatch.setattr("core.portfolio_builder.fetch_price_series", fake_fetch_price_series)


@pytest.mark.unit
def test_build_portfolio_long():
    weights = {"AAPL": 1.0}
    sides = {"AAPL": "L"}
    series = build_portfolio_series(weights, sides, "2020-01-01", "2020-01-10")
    assert isinstance(series, pd.Series)
    assert series.iloc[0] == pytest.approx(10000.0, rel=1e-2)
    assert series.iloc[-1] > series.iloc[0]


@pytest.mark.unit
def test_build_portfolio_short(monkeypatch):
    weights = {"AAPL": 1.0}
    sides = {"AAPL": "S"}
    series = build_portfolio_series(weights, sides, "2020-01-01", "2020-01-05")
    assert series.iloc[0] == pytest.approx(10000.0, rel=1e-2)
    assert series.iloc[-1] < series.iloc[0]
