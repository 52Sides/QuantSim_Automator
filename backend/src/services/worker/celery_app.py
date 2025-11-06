from celery import Celery
from celery.schedules import crontab

from core.config import settings


celery_app = Celery(
    "quantsim",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.update(
    broker_connection_retry_on_startup=True,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    task_track_started=True,
    task_time_limit=600,
)


@celery_app.task(name="ping")
def ping():
    return "pong"


celery_app.conf.beat_schedule = {
    "vacuum-analyze-db-nightly": {
        "task": "vacuum_analyze_task",
        "schedule": crontab(hour=3, minute=0),
    },
    "cluster-asset-prices-monthly": {
        "task": "cluster_asset_prices_task",
        "schedule": crontab(day_of_month=1, hour=4, minute=0),
    },
}
