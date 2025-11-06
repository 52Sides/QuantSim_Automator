from celery import Celery
import os

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

celery_app = Celery(
    "quantsim",
    broker=REDIS_URL,
    backend=REDIS_URL,
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
    """Простейшая проверка, что Celery работает"""
    return "pong"
