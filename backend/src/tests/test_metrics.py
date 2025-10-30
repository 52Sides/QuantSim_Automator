import pandas as pd
import numpy as np
import pytest
from core.portfolio_simulator import PortfolioSimulator


# ---- Вспомогательная функция ----
def make_price_series(days: int = 252, start_price: float = 100, daily_return: float = 0.001) -> pd.Series:
    """Создаёт синтетический временной ряд."""
    dates = pd.date_range("2020-01-01", periods=days, freq="B")
    prices = pd.Series(start_price * (1 + daily_return) ** np.arange(days), index=dates)
    return prices


# ---- Тест 1: базовые метрики ----
def test_basic_metrics_positive_growth():
    prices = make_price_series()
    sim = PortfolioSimulator(prices)
    result = sim.run()

    assert result.cagr > 0
    assert 0 <= result.max_drawdown < 1
    assert not np.isnan(result.sharpe)


# ---- Тест 2: стагнация (цены не меняются) ----
def test_zero_growth_sharpe_is_nan():
    prices = pd.Series([100.0] * 100, index=pd.date_range("2020-01-01", periods=100))
    sim = PortfolioSimulator(prices)
    result = sim.run()
    assert abs(result.cagr) < 1e-6
    assert np.isnan(result.sharpe) or abs(result.sharpe) < 1e-6


# ---- Тест 3: падение цен ----
def test_negative_growth():
    prices = make_price_series(days=200, daily_return=-0.001)
    sim = PortfolioSimulator(prices)
    result = sim.run()
    assert result.cagr < 0
    assert result.max_drawdown >= 0


# ---- Тест 4: обработка пустого ряда ----
def test_empty_series_raises():
    empty_series = pd.Series(dtype=float)
    with pytest.raises(Exception):
        PortfolioSimulator(empty_series)
