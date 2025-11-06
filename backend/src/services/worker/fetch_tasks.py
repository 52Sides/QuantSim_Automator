import yfinance as yf
import pandas as pd
from celery import shared_task
import psycopg2
from psycopg2.extras import execute_values
from core.config import settings
import logging
from services.redis.cache import sync_push_prices_to_redis

logger = logging.getLogger(__name__)

SYNC_DB_URL = settings.DATABASE_URL.replace("+asyncpg", "")
INSERT_SQL = """
INSERT INTO asset_prices (ticker, date, open, high, low, close, volume, inserted_at)
VALUES %s
ON CONFLICT (ticker, date)
DO UPDATE SET open = EXCLUDED.open, high = EXCLUDED.high, low = EXCLUDED.low,
              close = EXCLUDED.close, volume = EXCLUDED.volume;
"""


def validate_price_df(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if df.empty:
        raise RuntimeError("Empty dataframe from yfinance")
    if "Close" not in df.columns:
        raise RuntimeError("No Close column in fetched data")
    df.index = pd.to_datetime(df.index)
    df = df.sort_index().drop_duplicates()
    df = df.dropna(subset=["Close"])
    return df


@shared_task(name="fetch_prices_task")
def fetch_prices_task(ticker: str, start: str, end: str) -> dict:
    """Sync task: fetch via yfinance and upsert into Postgres using psycopg2 bulk insert.
       After DB upsert it also pushes rows into Redis for fast access."""

    logger.info(f"[fetch_prices_task] Fetch {ticker} {start} -> {end}")
    df = yf.download(ticker, start=start, end=end, progress=False, auto_adjust=False)
    df = validate_price_df(df)

    rows = [
        (
            ticker,
            dt.date(),
            float(row["Open"]) if not pd.isna(row["Open"]) else None,
            float(row["High"]) if not pd.isna(row["High"]) else None,
            float(row["Low"]) if not pd.isna(row["Low"]) else None,
            float(row["Close"]),
            float(row["Volume"]) if not pd.isna(row["Volume"]) else None,
        )
        for dt, row in df.iterrows()
    ]

    conn = psycopg2.connect(SYNC_DB_URL)
    try:
        with conn:
            with conn.cursor() as cur:
                execute_values(cur, INSERT_SQL, rows, template=None, page_size=1000)
        logger.info(f"[fetch_prices_task] Inserted {len(rows)} rows into DB for {ticker}")
    finally:
        conn.close()

    # push into Redis (sync)
    pushed = sync_push_prices_to_redis(ticker, df)
    logger.info(f"[fetch_prices_task] Pushed {pushed} rows into Redis for {ticker}")

    return {"ticker": ticker, "rows_db": len(rows), "rows_redis": pushed}
