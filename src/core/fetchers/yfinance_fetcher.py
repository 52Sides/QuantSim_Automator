from typing import Optional
import pandas as pd
import yfinance as yf

def fetch_price_series(ticker: str, start: str, end: str) -> pd.Series:
    """
    Загружает котировки с Yahoo Finance или генерирует синтетические данные.
    """
    df = yf.download(ticker, start=start, end=end, progress=False, auto_adjust=False)

    if df.empty:
        raise RuntimeError(f"No data for {ticker} between {start} and {end}")

    df = df.rename(columns={"Close": "close"})
    series = df["close"]

    # Гарантируем, что это именно Series, а не DataFrame
    if isinstance(series, pd.DataFrame):
        series = series.iloc[:, 0]

    # Убедимся, что индекс — даты
    if not isinstance(series.index, pd.DatetimeIndex):
        series.index = pd.to_datetime(series.index)

    series.name = "close"
    return series
