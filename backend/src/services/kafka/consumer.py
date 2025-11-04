import asyncio
import json
import logging
from aiokafka import AIOKafkaConsumer
from services.worker.tasks import run_simulation_task
from services.redis.pubsub import AsyncRedisPubSub
from core.config import settings
from db.database import AsyncSessionLocal
from db.models.metric_model import MetricModel

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


async def consume_simulation_requests():
    """Слушает команды симуляции и запускает Celery-задачи."""
    consumer = AIOKafkaConsumer(
        settings.KAFKA_SIMULATION_TOPIC,
        bootstrap_servers=settings.KAFKA_BROKER,
        group_id="simulation_workers",
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    )
    await consumer.start()
    try:
        async for msg in consumer:
            cmd = msg.value.get("command")
            if cmd:
                logger.info(f"Received simulation command: {cmd}")
                run_simulation_task.delay(cmd)
    finally:
        await consumer.stop()


async def consume_metrics_events():
    """Обновляет метрики в БД при получении событий metrics-events."""
    consumer = AIOKafkaConsumer(
        "metrics-events",
        bootstrap_servers=settings.KAFKA_BROKER,
        group_id="metrics_updater",
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    )
    await consumer.start()
    logger.info("Started metrics-events consumer")

    try:
        async for msg in consumer:
            data = msg.value
            portfolio_id = data.get("portfolio_id")
            sharpe = data.get("sharpe")
            drawdown = data.get("drawdown")

            if not portfolio_id:
                logger.warning(f"Skipping invalid metric message: {data}")
                continue

            async with AsyncSessionLocal() as session:
                metric = await session.get(MetricModel, portfolio_id)
                if metric:
                    metric.sharpe = sharpe
                    metric.drawdown = drawdown
                    await session.commit()
                    logger.info(f"Updated metrics for portfolio_id={portfolio_id}")
    except Exception as e:
        logger.exception(f"Metrics consumer error: {e}")
    finally:
        await consumer.stop()


# Kafka → Redis Bridge: пересылка событий симуляций фронтенду через WebSocket
async def consume_simulation_events():
    consumer = AIOKafkaConsumer(
        "portfolio-events",
        bootstrap_servers=settings.KAFKA_BROKER,
        group_id="simulation_events_bridge",
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    )
    await consumer.start()
    pubsub = AsyncRedisPubSub(settings.REDIS_URL, settings.REDIS_PUBSUB_CHANNEL)
    await pubsub.connect()
    logger.info("Started portfolio-events → Redis bridge")

    try:
        async for msg in consumer:
            event = msg.value
            event_type = event.get("type")
            if event_type == "simulation.completed":
                await pubsub.publish(event)
                logger.info(f"Published event to Redis: {event}")
    except Exception as e:
        logger.exception(f"Bridge consumer error: {e}")
    finally:
        await consumer.stop()
        await pubsub.close()
        logger.info("Stopped portfolio-events bridge")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(consume_simulation_requests())
    loop.create_task(consume_metrics_events())
    loop.create_task(consume_simulation_events())
    loop.run_forever()
