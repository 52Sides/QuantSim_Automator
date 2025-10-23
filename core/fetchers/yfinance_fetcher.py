from typing import Optional
import pandas as pd

# В реальной версии будем использовать yfinance или aiohttp. Сейчас - простая заглушка
def fetch_price_series(ticker: str, start: str, end: str) -> pd.Series:
    """
    Функция возвращает pd.Series с ценами закрытия (index = DatetimeIndex).
    Для MVP — генерируем синтетические данные или можно подключить yfinance.
    """
    try:
        import yfinance as yf
    except Exception:
        # если yfinance не установлен — вернём синтетический ряд для обучения
        dates = pd.date_range(start=start, end=end, freq="B")
        # синусоидальная + шум (чтобы метрики работали)
        prices = 100 + (pd.Series(range(len(dates))) * 0.01).values
        return pd.Series(prices, index=dates, name="close")

    # реальное получение данных:
    df = yf.download(ticker, start=start, end=end, progress=False)
    if df.empty:
        raise RuntimeError(f"No data for {ticker} between {start} and {end}")
    return df["Close"].rename("close")
