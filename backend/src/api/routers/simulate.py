from datetime import datetime, UTC
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from schemas.simulation import SimulationRequest, SimulationResponse, PortfolioPoint
from core import parse_command_safe, build_portfolio_series, PortfolioSimulator
from db.database import get_db
from db.models import AssetModel, SimulationModel, MetricModel

router = APIRouter(prefix="/simulate", tags=["Simulation"])


@router.post("/", response_model=SimulationResponse)
async def simulate_portfolio(request: SimulationRequest, db: AsyncSession = Depends(get_db)):
    """Симулирует портфель и сохраняет результат в БД."""

    try:
        # --- 1. Парсим команду ---
        weights, sides, start, end = parse_command_safe(request.command)
        tickers = list(weights.keys())

        # --- 2. Строим портфель ---
        portfolio_series = build_portfolio_series(weights, sides, start, end, budget=10_000)

        # --- 3. Считаем метрики ---
        simulator = PortfolioSimulator(portfolio_series)
        result = simulator.run()

        portfolio_points = [
            PortfolioPoint(date=idx.strftime("%Y-%m-%d"), portfolio_value=float(val))
            for idx, val in result.cumulative.items()
        ]

        # --- 4. Сохраняем активы ---
        assets = []
        for ticker in tickers:
            stmt = await db.execute(
                AssetModel.__table__.select().where(AssetModel.ticker == ticker)
            )
            existing = stmt.scalar_one_or_none()
            if existing:
                assets.append(existing)
            else:
                new_asset = AssetModel(ticker=ticker, name=None)
                db.add(new_asset)
                await db.flush()
                assets.append(new_asset)

        # --- 5. Сохраняем симуляцию ---
        simulation = SimulationModel(
            command=request.command,
            start_date=start,
            end_date=end,
            result_json=[p.model_dump() for p in portfolio_points],
            created_at=datetime.now(UTC),
            assets=assets,
        )
        db.add(simulation)
        await db.flush()

        # --- 6. Сохраняем метрики ---
        metrics = MetricModel(
            simulation_id=simulation.id,
            cagr=result.cagr,
            sharpe=result.sharpe,
            max_drawdown=result.max_drawdown,
            created_at=datetime.now(UTC),
        )
        db.add(metrics)
        await db.commit()

        # --- 7. Возврат ответа (тот же формат) ---
        return SimulationResponse(
            cagr=result.cagr,
            sharpe=result.sharpe,
            max_drawdown=result.max_drawdown,
            portfolio=portfolio_points,
        )

    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))
