from celery import shared_task
import psycopg2
from core.config import settings
import logging

logger = logging.getLogger(__name__)

SYNC_DB_URL = settings.DATABASE_URL.replace("+asyncpg", "")

@shared_task(name="vacuum_analyze_task")
def vacuum_analyze_task():
    """Performs VACUUM ANALYZE on asset_prices."""
    conn = psycopg2.connect(SYNC_DB_URL)
    try:
        with conn.cursor() as cur:
            logger.info("Running VACUUM (VERBOSE, ANALYZE)...")
            cur.execute("VACUUM (VERBOSE, ANALYZE) asset_prices;")
        conn.commit()
        logger.info("VACUUM completed successfully.")
    finally:
        conn.close()

@shared_task(name="cluster_asset_prices_task")
def cluster_asset_prices_task():
    """Reclusters asset_prices table by index once a month."""
    conn = psycopg2.connect(SYNC_DB_URL)
    try:
        with conn.cursor() as cur:
            logger.info("Running CLUSTER asset_prices USING ix_asset_ticker_date...")
            cur.execute("CLUSTER asset_prices USING ix_asset_ticker_date;")
        conn.commit()
        logger.info("CLUSTER completed successfully.")
    finally:
        conn.close()
