import numpy as np
import pandas as pd
from typing import Dict, Any
from core.simulation_result import SimulationResult


class PortfolioSimulator:
    """Вычисляет метрики эффективности портфеля."""

    def __init__(self, price_series: pd.Series, risk_free_rate: float = 0.0):
        if not isinstance(price_series, pd.Series):
            raise TypeError("price_series must be a pandas Series")
        if price_series.empty:
            raise ValueError("price_series is empty")
        self.prices = price_series.sort_index()
        self.risk_free_rate = risk_free_rate

    def daily_returns(self) -> pd.Series:
        return self.prices.pct_change().dropna()

    def cumulative_returns(self) -> pd.Series:
        rets = self.daily_returns()
        return (1 + rets).cumprod() - 1

    def cagr(self) -> float:
        start, end = self.prices.iloc[0], self.prices.iloc[-1]
        days = (self.prices.index[-1] - self.prices.index[0]).days
        years = max(days / 365.25, 1 / 365.25)
        return (end / start) ** (1 / years) - 1

    def sharpe_ratio(self, returns: pd.Series) -> float:
        excess = returns - (self.risk_free_rate / 252)
        if excess.std() == 0:
            return float("nan")
        ann_mean = excess.mean() * 252
        ann_std = excess.std() * np.sqrt(252)
        return ann_mean / ann_std

    def max_drawdown(self, cumulative: pd.Series) -> float:
        running_max = (1 + cumulative).cummax()
        drawdown = (1 + cumulative) / running_max - 1
        return abs(drawdown.min())

    def run(self, meta: Dict[str, Any] = None) -> SimulationResult:
        meta = meta or {}
        rets = self.daily_returns()
        cum = self.cumulative_returns()
        return SimulationResult(
            returns=rets,
            cumulative=cum,
            cagr=self.cagr(),
            sharpe=self.sharpe_ratio(rets),
            max_drawdown=self.max_drawdown(cum),
            meta=meta,
        )
