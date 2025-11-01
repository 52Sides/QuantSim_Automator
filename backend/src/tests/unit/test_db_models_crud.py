import datetime
import pytest

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from db.models import AssetModel, SimulationModel, MetricModel


@pytest.mark.unit
@pytest.mark.asyncio
async def test_asset_crud(db_session: AsyncSession):
    asset = AssetModel(ticker="AAPL", name="Apple Inc.")
    db_session.add(asset)
    await db_session.commit()

    result = await db_session.get(AssetModel, asset.id)
    assert result.ticker == "AAPL"

    await db_session.delete(result)
    await db_session.commit()
    assert await db_session.get(AssetModel, asset.id) is None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_simulation_and_metrics(db_session: AsyncSession):
    sim = SimulationModel(
        command="AAPL-L-100% 2020-01-01 2021-01-01",
        start_date=datetime.date(2020, 1, 1),
        end_date=datetime.date(2021, 1, 1),
        result_json=[{"date": "2020-01-02", "portfolio_value": 1.0}],
    )
    db_session.add(sim)
    await db_session.flush()

    metric = MetricModel(simulation_id=sim.id, cagr=0.1, sharpe=1.2, max_drawdown=-0.2)
    db_session.add(metric)
    await db_session.commit()

    # Загружаем модель с подгрузкой связей
    stmt = select(SimulationModel).options(selectinload(SimulationModel.metrics)).where(SimulationModel.id == sim.id)
    result = await db_session.execute(stmt)
    db_obj = result.scalar_one()

    assert db_obj.metrics.cagr == 0.1
