from celery import shared_task, group, chord
from core import parse_command_safe
from core.prices import load_prices_from_db_to_redis
from db.database import AsyncSessionLocal
from db.models import SimulationModel
from services.reports import generate_xlsx_report
from services.reports_cache import set_report_status
from services.worker.fetch_tasks import fetch_prices_task
import psycopg2
from datetime import date
from core.config import settings
import asyncio
import logging

logger = logging.getLogger(__name__)

SYNC_DB_URL = settings.DATABASE_URL.replace("+asyncpg", "")


def get_missing_date_ranges_sync_wrapper(ticker: str, start: str, end: str) -> bool:
    """Sync check: returns True if there are missing days for ticker."""
    conn = psycopg2.connect(SYNC_DB_URL)
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT COUNT(1) FROM asset_prices WHERE ticker=%s AND date BETWEEN %s AND %s",
                (ticker, start, end)
            )
            count = cur.fetchone()[0]
    finally:
        conn.close()

    needed_days = (date.fromisoformat(end) - date.fromisoformat(start)).days + 1
    return count < needed_days


@shared_task(name="run_simulation_task")
def run_simulation_task(command: str, user_id: int | None = None):
    # 1) parse
    weights, sides, start, end = parse_command_safe(command)
    tickers = list(weights.keys())

    # 2) For each ticker: load DB rows into Redis (async) and detect missing via sync check
    # push available DB rows into Redis first so partial data already in redis
    async def _prepare_redis():
        async with AsyncSessionLocal() as db:
            for t in tickers:
                # load available DB rows to redis
                await load_prices_from_db_to_redis(db, t, start, end)
    # run preparation
    asyncio.run(_prepare_redis())

    # 3) now detect missing tickers via sync check
    missing = [t for t in tickers if get_missing_date_ranges_sync_wrapper(t, start, end)]

    if missing:
        # start fetch tasks, after all done continue_simulation
        fetch_group = group(fetch_prices_task.s(t, start, end) for t in missing)
        chord(fetch_group)(continue_simulation_task.s(command, user_id))
        return {"status": "queued_for_fetch", "missing": missing}
    else:
        # all data now present in Redis - continue immediately
        return continue_simulation_task(command, user_id)


@shared_task(name="continue_simulation_task")
def continue_simulation_task(command: str, user_id: int | None = None):
    # call async runner that reads from Redis
    import asyncio
    from services.worker.simulation_runner import run_simulation_async
    return asyncio.run(run_simulation_async(command, user_id))


@shared_task(name="generate_report_task")
def generate_report_task(simulation_id: int):
    async def _inner():
        await set_report_status(simulation_id, "running")
        async with AsyncSessionLocal() as db:
            sim = await db.get(SimulationModel, simulation_id)
            if not sim:
                await set_report_status(simulation_id, "error")
                return
            path = await generate_xlsx_report(sim)
            await set_report_status(simulation_id, "ready", str(path))
    asyncio.run(_inner())