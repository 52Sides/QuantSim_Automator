import pandas as pd
import yfinance as yf

def fetch_ticker_data(ticker: str, start: str, end: str) -> pd.DataFrame:
    """Загружает котировки с Yahoo Finance"""
    df = yf.download(ticker, start=start, end=end, progress=False, auto_adjust=False)
    if df.empty:
        raise RuntimeError(f"No data for {ticker} between {start} and {end}")

    df = df[['Open', 'High', 'Low', 'Close', 'Volume']]
    df.index = pd.to_datetime(df.index)
    df = df.sort_index().drop_duplicates()
    return df
