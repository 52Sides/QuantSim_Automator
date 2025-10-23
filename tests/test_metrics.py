import pandas as pd
import numpy as np
from core.portfolio import PortfolioSimulator

def test_cagr_sharpe_drawdown():
    # синтетический ряд: экспоненциальный рост (CAGR > 0), нет волатильности -> Sharpe = nan or inf guard
    dates = pd.date_range("2020-01-01", periods=252*2, freq="B")
    # создаём линейно растущие цены
    prices = pd.Series(100 * (1 + 0.0005) ** np.arange(len(dates)), index=dates)
    sim = PortfolioSimulator(prices)
    result = sim.run()
    assert result.cagr > 0
    assert result.max_drawdown >= 0
    # Sharpe может быть nan если std == 0, но должен не выбрасывать исключение
