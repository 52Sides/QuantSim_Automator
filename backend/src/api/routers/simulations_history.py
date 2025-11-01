from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from db.database import get_db
from db.models import SimulationModel, MetricModel, AssetModel  # noqa: F401

router = APIRouter(prefix="/simulations_history", tags=["Simulations_history"])


@router.get("/")
async def list_simulations_history(
    db: AsyncSession = Depends(get_db),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """
    Получить список симуляций (пагинация, последние по времени).
    """
    stmt = (
        select(SimulationModel)
        .options(selectinload(SimulationModel.metrics), selectinload(SimulationModel.assets))
        .order_by(SimulationModel.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    result = await db.execute(stmt)
    simulations = result.scalars().unique().all()

    return [
        {
            "id": s.id,
            "command": s.command,
            "start_date": s.start_date,
            "end_date": s.end_date,
            "created_at": s.created_at,
            "cagr": s.metrics.cagr if s.metrics else None,
            "sharpe": s.metrics.sharpe if s.metrics else None,
            "max_drawdown": s.metrics.max_drawdown if s.metrics else None,
            "assets": [a.ticker for a in s.assets],
        }
        for s in simulations
    ]


@router.get("/{simulation_id}")
async def get_simulations_history(simulation_id: int, db: AsyncSession = Depends(get_db)):
    """
    Получить полную информацию по конкретной симуляции (с портфелем и метриками).
    """
    stmt = (
        select(SimulationModel)
        .where(SimulationModel.id == simulation_id)
        .options(selectinload(SimulationModel.metrics), selectinload(SimulationModel.assets))
    )
    result = await db.execute(stmt)
    simulation = result.scalar_one_or_none()

    if not simulation:
        raise HTTPException(status_code=404, detail="Simulation not found")

    return {
        "id": simulation.id,
        "command": simulation.command,
        "start_date": simulation.start_date,
        "end_date": simulation.end_date,
        "created_at": simulation.created_at,
        "assets": [a.ticker for a in simulation.assets],
        "metrics": {
            "cagr": simulation.metrics.cagr if simulation.metrics else None,
            "sharpe": simulation.metrics.sharpe if simulation.metrics else None,
            "max_drawdown": simulation.metrics.max_drawdown if simulation.metrics else None,
        },
        "portfolio": simulation.result_json,  # сохранённый JSON-ряд
    }
