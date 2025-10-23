from __future__ import annotations
from dataclasses import dataclass
import pandas as pd
import numpy as np
from typing import Dict, Any


@dataclass
class SimulationResult:
    returns: pd.Series           # дневные доходности
    cumulative: pd.Series        # накопленная доходность
    cagr: float
    sharpe: float
    max_drawdown: float
    meta: Dict[str, Any]


class PortfolioSimulator:
    """
    Класс-симулятор: получает временной ряд цен (pd.Series или DataFrame с 'close'),
    вычисляет дневные доходности, метрики и возвращает SimulationResult.
    """

    def __init__(self, price_series: pd.Series, risk_free_rate: float = 0.0):
        if not isinstance(price_series, pd.Series):
            raise TypeError("price_series must be a pandas Series of prices indexed by date")

        self.prices = price_series.sort_index()
        self.risk_free_rate = risk_free_rate

    def daily_returns(self) -> pd.Series:
        # Простая дневная доходность: pct_change
        rets = self.prices.pct_change().dropna()
        return rets

    def cumulative_returns(self) -> pd.Series:
        rets = self.daily_returns()
        cum = (1 + rets).cumprod() - 1
        return cum

    def cagr(self) -> float:
        # CAGR = (ending_value / starting_value)^(1/years) - 1
        start, end = self.prices.iloc[0], self.prices.iloc[-1]
        days = (self.prices.index[-1] - self.prices.index[0]).days
        years = days / 365.25 if days > 0 else 1/365.25
        return (end / start) ** (1 / years) - 1

    def sharpe_ratio(self, returns: pd.Series) -> float:
        # неаннуализированный Sharpe => annualize by sqrt(252)
        excess = returns - (self.risk_free_rate / 252)
        if excess.std() == 0:
            return float("nan")
        ann_mean = excess.mean() * 252
        ann_std = excess.std() * np.sqrt(252)
        return ann_mean / ann_std

    def max_drawdown(self, cumulative: pd.Series) -> float:
        # maximum drawdown from cumulative returns (values like 0.2 => +20%)
        running_max = (1 + cumulative).cummax()
        drawdown = (1 + cumulative) / running_max - 1
        md = drawdown.min()
        return abs(md)

    def run(self, meta: Dict[str, Any] = None) -> SimulationResult:
        meta = meta or {}
        rets = self.daily_returns()
        cum = self.cumulative_returns()
        result = SimulationResult(
            returns=rets,
            cumulative=cum,
            cagr=self.cagr(),
            sharpe=self.sharpe_ratio(rets),
            max_drawdown=self.max_drawdown(cum),
            meta=meta,
        )
        return result
