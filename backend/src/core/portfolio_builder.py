import pandas as pd
from typing import Dict

from core.fetchers.yfinance_fetcher import fetch_ticker_data


def build_portfolio_series(
    weights: Dict[str, float],
    sides: Dict[str, str],
    start: str,
    end: str,
    budget: float = 10_000.0
) -> pd.Series:
    """Строит ряд стоимости портфеля на основе весов и сторон."""

    data = {}
    for ticker, weight in weights.items():
        s = fetch_ticker_data(ticker, start, end)
        if s.empty:
            raise ValueError(f"No data for {ticker}")
        if sides[ticker] == "S":  # short
            s = s.iloc[0] * (s.iloc[0] / s)
        data[ticker] = s

    df = pd.DataFrame(data).dropna()
    first = df.iloc[0]
    value_df = df.div(first) * pd.Series(weights) * budget
    portfolio_value = value_df.sum(axis=1)

    return portfolio_value  # в USD, не нормализовано
