import pandas as pd
import pytest
import yfinance as yf
from core.fetchers.yfinance_fetcher import fetch_ticker_data


def test_fetch_price_series_returns_series(monkeypatch):
    """Проверяем, что функция возвращает Series с правильными данными."""
    # Подменяем yf.download фиктивными данными
    def fake_download(*args, **kwargs):
        dates = pd.date_range("2024-01-01", periods=3)
        return pd.DataFrame({"Close": [10, 20, 30]}, index=dates)

    monkeypatch.setattr(yf, "download", fake_download)

    result = fetch_ticker_data("AAPL", "2024-01-01", "2024-01-03")

    assert isinstance(result, pd.Series)
    assert result.name == "close"
    assert list(result.values) == [10, 20, 30]
    assert isinstance(result.index, pd.DatetimeIndex)


def test_fetch_price_series_empty_data(monkeypatch):
    """Проверяем, что при пустых данных выбрасывается RuntimeError."""
    monkeypatch.setattr(yf, "download", lambda *a, **k: pd.DataFrame())

    with pytest.raises(RuntimeError):
        fetch_ticker_data("AAPL", "2024-01-01", "2024-01-03")
