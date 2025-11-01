import pandas as pd
import numpy as np
import pytest
from core.portfolio_simulator import PortfolioSimulator


@pytest.fixture
def price_series():
    idx = pd.date_range("2020-01-01", "2020-12-31", freq="B")
    prices = pd.Series(100 * (1 + 0.001) ** np.arange(len(idx)), index=idx)
    return prices


def test_simulator_basic_metrics(price_series):
    sim = PortfolioSimulator(price_series)
    result = sim.run()
    assert result.cagr > 0
    assert not np.isnan(result.sharpe)
    assert 0 <= result.max_drawdown <= 1


def test_simulator_zero_variance():
    idx = pd.date_range("2020-01-01", "2020-03-01")
    prices = pd.Series(100.0, index=idx)
    sim = PortfolioSimulator(prices)
    res = sim.run()
    assert np.isnan(res.sharpe)
    assert res.cagr == pytest.approx(0.0)


def test_simulator_invalid_input():
    with pytest.raises(TypeError):
        PortfolioSimulator("not a series")
    with pytest.raises(ValueError):
        PortfolioSimulator(pd.Series(dtype=float))
