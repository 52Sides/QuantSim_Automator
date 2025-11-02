from datetime import datetime
from celery import shared_task
from core import parse_command_safe, build_portfolio_series, PortfolioSimulator
from db.database import AsyncSessionLocal
from db.models import SimulationModel, MetricModel, AssetModel
from schemas.simulation import PortfolioPoint

@shared_task(name="run_simulation_task")
def run_simulation_task(command: str) -> dict:
    """
    Фоновая задача для симуляции портфеля.
    Работает синхронно, но вызывается Celery.
    """
    try:
        # 1. Парсим команду
        weights, sides, start, end = parse_command_safe(command)
        tickers = list(weights.keys())

        # 2. Строим портфель
        portfolio_series = build_portfolio_series(weights, sides, start, end, budget=10_000)

        # 3. Считаем метрики
        simulator = PortfolioSimulator(portfolio_series)
        result = simulator.run()

        # 4. Преобразуем результат
        portfolio_points = [
            PortfolioPoint(date=idx.strftime("%Y-%m-%d"), portfolio_value=float(val)).model_dump()
            for idx, val in result.cumulative.items()
        ]

        # 5. Сохраняем в базу
        import asyncio
        async def _save():
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
                    created_at=datetime.now(datetime.UTC),
                    assets=assets,
                )
                db.add(sim)
                await db.flush()

                metrics = MetricModel(
                    simulation_id=sim.id,
                    cagr=result.cagr,
                    sharpe=result.sharpe,
                    max_drawdown=result.max_drawdown,
                    created_at=datetime.now(datetime.UTC),
                )
                db.add(metrics)
                await db.commit()

        asyncio.run(_save())

        return {
            "status": "SUCCESS",
            "cagr": result.cagr,
            "sharpe": result.sharpe,
            "max_drawdown": result.max_drawdown,
            "portfolio": portfolio_points,
        }

    except Exception as e:
        return {"status": "FAILURE", "error": str(e)}
