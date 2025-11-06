from typing import Tuple
import pandas as pd
from sqlalchemy import select, insert, func
from db.models.asset_price_model import AssetPriceModel
from db.database import AsyncSessionLocal
from core.config import settings


async def get_db_price_count(db, ticker: str, start: str, end: str) -> int:
    stmt = select(func.count()).select_from(AssetPriceModel).where(
        AssetPriceModel.ticker == ticker,
        AssetPriceModel.date >= start,
        AssetPriceModel.date <= end
    )
    res = await db.execute(stmt)
    (count,) = res.one()
    return count


async def get_price_series_from_db(db, ticker: str, start_date: str, end_date: str) -> pd.Series:
    stmt = select(AssetPriceModel).where(
        AssetPriceModel.ticker == ticker,
        AssetPriceModel.date >= start_date,
        AssetPriceModel.date <= end_date
    ).order_by(AssetPriceModel.date)
    res = await db.execute(stmt)
    rows = res.scalars().all()
    if not rows:
        return pd.Series(dtype="float64")  # empty
    dates = [r.date for r in rows]
    closes = [r.close for r in rows]
    s = pd.Series(data=closes, index=pd.to_datetime(dates))
    s.name = "close"
    return s


async def get_missing_date_ranges(db, ticker: str, start_date, end_date) -> Tuple[str,str] or None:
    """Возвращает интервалы дат, которые отсутствуют в БД (упрощённо).
       Можно расширить до списка интервалов для больших разрывов."""
    stmt = select(
        func.min(AssetPriceModel.date),
        func.max(AssetPriceModel.date)
    ).where(AssetPriceModel.ticker == ticker)
    res = await db.execute(stmt)
    min_date, max_date = res.one_or_none() or (None, None)

    # простая логика: если нет данных или покрытие не включает start..end -> запросим весь диапазон
    if not min_date or not max_date:
        return (start_date, end_date)

    if min_date > start_date or max_date < end_date:
        # для простоты — запросим недостающий диапазон целиком
        return (start_date, end_date)

    return None


async def upsert_prices_bulk(db, ticker: str, df: pd.DataFrame):
    """df expected to have index as dates and column 'Close' (or 'close')."""
    df = df.copy()
    if "Close" in df.columns:
        df = df.rename(columns={"Close": "close"})

    df["date"] = pd.to_datetime(df.index).date
    rows = []

    for _, r in df.iterrows():
        rows.append({
            "ticker": ticker,
            "date": r["date"],
            "open": float(r.get("Open", None)) if r.get("Open", None) is not None else None,
            "high": float(r.get("High", None)) if r.get("High", None) is not None else None,
            "low": float(r.get("Low", None)) if r.get("Low", None) is not None else None,
            "close": float(r["close"]),
            "volume": float(r.get("Volume", None)) if r.get("Volume", None) is not None else None,
        })

    # Используем bulk insert with ON CONFLICT DO UPDATE
    from sqlalchemy.dialects.postgresql import insert as pg_insert

    stmt = pg_insert(AssetPriceModel.__table__).values(rows)
    update_cols = {c.name: stmt.excluded[c.name] for c in AssetPriceModel.__table__.columns if c.name not in ('id', 'ticker', 'date')}
    stmt = stmt.on_conflict_do_update(
        index_elements=['ticker', 'date'],
        set_=update_cols
    )
    await db.execute(stmt)
    await db.commit()


async def load_prices_from_db_to_redis(db, ticker: str, start: str, end: str):
    """
    Загружает доступные строки из БД и пушит их в Redis.
    Возвращает количество загруженных строк.
    """
    from services.redis.cache import push_prices_to_redis

    stmt = select(AssetPriceModel).where(
        AssetPriceModel.ticker == ticker,
        AssetPriceModel.date >= start,
        AssetPriceModel.date <= end
    ).order_by(AssetPriceModel.date)

    res = await db.execute(stmt)
    rows = res.scalars().all()
    if not rows:
        return 0

    data, dates = [], []
    for r in rows:
        dates.append(r.date)
        data.append({
            "Open": r.open,
            "High": r.high,
            "Low": r.low,
            "Close": r.close,
            "Volume": r.volume,
        })

    import pandas as pd
    df = pd.DataFrame(data, index=pd.to_datetime(dates))
    return await push_prices_to_redis(ticker, df)
