from __future__ import annotations
from dataclasses import dataclass
import pandas as pd
import numpy as np
from typing import Dict, Any


@dataclass
class SimulationResult:
    """Результат симуляции."""
    returns: pd.Series
    cumulative: pd.Series
    cagr: float
    sharpe: float
    max_drawdown: float
    meta: Dict[str, Any]


class PortfolioSimulator:
    """
    Класс, выполняющий симуляцию портфеля по ряду цен.
    Он вычисляет основные метрики эффективности инвестиций.
    """

    def __init__(self, price_series: pd.Series, risk_free_rate: float = 0.0):
        if not isinstance(price_series, pd.Series):
            raise TypeError("price_series must be a pandas Series of prices indexed by date")
        self.prices = price_series.sort_index()
        self.risk_free_rate = risk_free_rate

    def daily_returns(self) -> pd.Series:
        """Вычисляем дневные доходности."""
        return self.prices.pct_change().dropna()

    def cumulative_returns(self) -> pd.Series:
        """Вычисляем накопленную доходность."""
        rets = self.daily_returns()
        return (1 + rets).cumprod() - 1

    def cagr(self) -> float:
        """Вычисляем CAGR (среднегодовой рост)."""
        start, end = self.prices.iloc[0], self.prices.iloc[-1]
        days = (self.prices.index[-1] - self.prices.index[0]).days
        years = days / 365.25 if days > 0 else 1 / 365.25
        return (end / start) ** (1 / years) - 1

    def sharpe_ratio(self, returns: pd.Series) -> float:
        """Вычисляем Sharpe Ratio."""
        excess = returns - (self.risk_free_rate / 252)
        if excess.std() == 0:
            return float("nan")
        ann_mean = excess.mean() * 252
        ann_std = excess.std() * np.sqrt(252)
        return ann_mean / ann_std

    def max_drawdown(self, cumulative: pd.Series) -> float:
        """Вычисляем максимальную просадку."""
        running_max = (1 + cumulative).cummax()
        drawdown = (1 + cumulative) / running_max - 1
        return abs(drawdown.min())

    def run(self, meta: Dict[str, Any] = None) -> SimulationResult:
        """Запускаем симуляцию и возвращаем результаты."""
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
