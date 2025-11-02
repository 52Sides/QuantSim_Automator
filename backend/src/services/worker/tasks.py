from datetime import datetime, UTC
from celery import shared_task
from core import parse_command_safe, build_portfolio_series, PortfolioSimulator
from db.database import AsyncSessionLocal
from db.models import SimulationModel, MetricModel, AssetModel
from schemas.simulation import PortfolioPoint
import asyncio
import json
import redis.asyncio as aioredis


@shared_task(name="run_simulation_task")
def run_simulation_task(command: str) -> dict:
    """
    Фоновая задача: симулирует портфель, публикует прогресс в Redis,
    сохраняет результат в базу.
    """
    async def _inner():
        # --- Инициализация Redis ---
        redis_client = aioredis.from_url("redis://redis:6379", decode_responses=True)
        task_key = f"simulation:{command}"
        await redis_client.hset(task_key, mapping={"status": "running", "progress": 0})

        try:
            # --- 1. Парсим команду ---
            await redis_client.hset(task_key, "progress", 10)
            weights, sides, start, end = parse_command_safe(command)
            tickers = list(weights.keys())

            # --- 2. Строим портфель ---
            await redis_client.hset(task_key, "progress", 40)
            portfolio_series = build_portfolio_series(weights, sides, start, end, budget=10_000)

            # --- 3. Считаем метрики ---
            await redis_client.hset(task_key, "progress", 70)
            simulator = PortfolioSimulator(portfolio_series)
            result = simulator.run()

            portfolio_points = [
                PortfolioPoint(date=idx.strftime("%Y-%m-%d"), portfolio_value=float(val)).model_dump()
                for idx, val in result.cumulative.items()
            ]

            # --- 4. Сохраняем результат в БД ---
            async with AsyncSessionLocal() as db:
                assets = []
                for ticker in tickers:
                    q = await db.execute(
                        AssetModel.__table__.select().where(AssetModel.ticker == ticker)
                    )
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

            # --- 5. Финал: публикуем успех ---
            payload = {
                "status": "done",
                "progress": 100,
                "result": {
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
            await redis_client.publish("simulations", json.dumps({"status": "error", "error": str(e)}))
            raise

    # В Celery-задаче запускаем асинхронно
    return asyncio.run(_inner())
