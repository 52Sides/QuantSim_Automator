import json
from datetime import datetime
from typing import Dict, List
import pandas as pd
import redis.asyncio as aioredis
import redis as redis_sync
from core.config import settings

REDIS_URL = settings.REDIS_URL


# --- Async API (for simulators / async runners) ---
async def async_redis_client():
    return aioredis.from_url(REDIS_URL, decode_responses=True)


async def load_prices_range_from_redis(ticker: str, start: str, end: str) -> pd.DataFrame:
    """
    Возвращает DataFrame из Redis для тикера и диапазона дат inclusive.
    Если некоторого дня нет — он просто пропущен (caller проверяет покрытие).
    """
    r = await async_redis_client()
    key = f"prices:{ticker}"
    # hgetall returns dict str->str
    mapping = await r.hgetall(key)
    if not mapping:
        return pd.DataFrame()  # empty

    # filter keys between start and end
    rows = []
    for date_str, json_str in mapping.items():
        if start <= date_str <= end:
            rows.append((date_str, json.loads(json_str)))
    if not rows:
        return pd.DataFrame()

    rows.sort(key=lambda x: x[0])
    df = pd.DataFrame([v for _, v in rows], index=pd.to_datetime([d for d, _ in rows]))

    return df


async def push_prices_to_redis(ticker: str, df: pd.DataFrame):
    """
    Записать DataFrame в Redis hash key `prices:{ticker}`. df index -> dates.
    """
    if df.empty:
        return 0

    r = await async_redis_client()
    key = f"prices:{ticker}"
    mapping = {}
    for dt, row in df.iterrows():
        date_key = dt.strftime("%Y-%m-%d")
        mapping[date_key] = json.dumps({
            "open": None if pd.isna(row.get("Open") or row.get("open")) else float(row.get("Open") or row.get("open")),
            "high": None if pd.isna(row.get("High") or row.get("high")) else float(row.get("High") or row.get("high")),
            "low": None if pd.isna(row.get("Low") or row.get("low")) else float(row.get("Low") or row.get("low")),
            "close": float(row.get("Close") or row.get("close")),
            "volume": None if pd.isna(row.get("Volume") or row.get("volume")) else float(row.get("Volume") or row.get("volume")),
        })
    if mapping:
        await r.hset(key, mapping=mapping)
        await r.hset(f"{key}:meta", mapping={"last_fetched_at": datetime.utcnow().isoformat()})
    return len(mapping)


# --- Sync API (для fetch_prices_task, который sync) ---
def sync_redis_client():
    return redis_sync.from_url(REDIS_URL, decode_responses=True)


def sync_push_prices_to_redis(ticker: str, df: pd.DataFrame):
    if df.empty:
        return 0
    r = sync_redis_client()
    key = f"prices:{ticker}"
    mapping = {}
    for dt, row in df.iterrows():
        date_key = dt.strftime("%Y-%m-%d")
        mapping[date_key] = json.dumps({
            "open": None if pd.isna(row.get("Open") or row.get("open")) else float(row.get("Open") or row.get("open")),
            "high": None if pd.isna(row.get("High") or row.get("high")) else float(row.get("High") or row.get("high")),
            "low": None if pd.isna(row.get("Low") or row.get("low")) else float(row.get("Low") or row.get("low")),
            "close": float(row.get("Close") or row.get("close")),
            "volume": None if pd.isna(row.get("Volume") or row.get("volume")) else float(row.get("Volume") or row.get("volume")),
        })
    if mapping:
        r.hset(key, mapping=mapping)
        r.hset(f"{key}:meta", mapping={"last_fetched_at": datetime.utcnow().isoformat()})
    return len(mapping)
