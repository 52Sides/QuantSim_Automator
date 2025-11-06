import pytest
from sqlalchemy.future import select
from db.models import SimulationModel
from services.kafka import consume_simulation_events

@pytest.mark.integration
@pytest.mark.asyncio
async def test_kafka_db_consistency(db_session):
    events = await consume_simulation_events(limit=10)
    for e in events:
        db_entry = await db_session.execute(
            select(SimulationModel).where(SimulationModel.id == e["id"])
        )
        assert db_entry.scalar_one_or_none(), f"Missing DB entry for {e['id']}"
