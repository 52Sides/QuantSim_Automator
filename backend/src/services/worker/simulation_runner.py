# backend/src/services/worker/simulation_runner.py
import asyncio
import json
from datetime import datetime, UTC
import redis.asyncio as aioredis
import pandas as pd

from core import parse_command_safe, build_portfolio_series, PortfolioSimulator
from db.database import AsyncSessionLocal
from db.models import SimulationModel, MetricModel, AssetModel
from schemas.simulation import PortfolioPoint
from core.config import settings
from services.redis.cache import load_prices_range_from_redis

REDIS_URL = settings.REDIS_URL

async def run_simulation_async(command: str, user_id: int | None = None) -> dict:
    redis_client = aioredis.from_url(REDIS_URL, decode_responses=True)
    task_key = f"simulation:{command}"
    await redis_client.hset(task_key, mapping={"status": "running", "progress": 0})

    try:
        # parse
        await redis_client.hset(task_key, "progress", 10)
        weights, sides, start, end = parse_command_safe(command)
        tickers = list(weights.keys())

        # prepare portfolio series by loading each ticker series from Redis
        await redis_client.hset(task_key, "progress", 40)
        series_map = {}
        for t in tickers:
            df = await load_prices_range_from_redis(t, start, end)
            if df.empty:
                # this should not happen if pipeline worked — raise for visibility
                raise RuntimeError(f"No price data in Redis for {t} {start}->{end}")
            # ensure DataFrame -> Series of close prices for portfolio builder
            if isinstance(df, pd.DataFrame):
                # ensure column case
                col = "Close" if "Close" in df.columns else "close"
                if col not in df.columns:
                    col = df.columns[0]
                s = df[col]
            else:
                s = df
            if not isinstance(s.index, pd.DatetimeIndex):
                s.index = pd.to_datetime(s.index)
            series_map[t] = s

        # build portfolio_series (this function should accept mapping of series)
        await redis_client.hset(task_key, "progress", 60)
        portfolio_series = build_portfolio_series(series_map, weights, sides, start, end, budget=10_000)

        # run simulator
        await redis_client.hset(task_key, "progress", 80)
        simulator = PortfolioSimulator(portfolio_series)
        result = simulator.run()

        portfolio_points = [
            PortfolioPoint(date=idx.strftime("%Y-%m-%d"), portfolio_value=float(val)).model_dump()
            for idx, val in result.cumulative.items()
        ]

        # persist results (async DB)
        async with AsyncSessionLocal() as db:
            assets = []
            for ticker in tickers:
                q = await db.execute(AssetModel.__table__.select().where(AssetModel.ticker == ticker))
                asset = q.scalar_one_or_none()
                if not asset:
                    asset = AssetModel(ticker=ticker, name=None)
                    db.add(asset)
                    await db.flush()
                assets.append(asset)

            sim = SimulationModel(
                command=command,
                start_date=start,
                end_date=end,
                result_json=portfolio_points,
                created_at=datetime.now(UTC),
                assets=assets,
                user_id=user_id,
            )
            db.add(sim)
            await db.flush()

            metrics = MetricModel(
                simulation_id=sim.id,
                cagr=result.cagr,
                sharpe=result.sharpe,
                max_drawdown=result.max_drawdown,
                created_at=datetime.now(UTC),
            )
            db.add(metrics)
            await db.commit()

        # publish final
        payload = {
            "status": "done",
            "progress": 100,
            "user_id": user_id,
            "result": {
                "simulation_id": sim.id,
                "cagr": result.cagr,
                "sharpe": result.sharpe,
                "max_drawdown": result.max_drawdown,
                "portfolio": portfolio_points,
            },
        }
        await redis_client.hset(task_key, mapping={"progress": 100, "status": "done"})
        await redis_client.publish("simulations", json.dumps(payload))
        return payload

    except Exception as e:
        await redis_client.hset(task_key, mapping={"status": "error", "error": str(e)})
        await redis_client.publish("simulations", json.dumps({"status": "error", "error": str(e), "user_id": user_id}))
        raise
