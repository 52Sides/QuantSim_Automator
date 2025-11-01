from celery import Celery
from core.config import settings

celery_app = Celery(
    "quant_sim_automator",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

@celery_app.task
def ping():
    return "pong"
