import asyncio
import json
import logging

from aiokafka import AIOKafkaConsumer

from core.config import settings
from db.database import AsyncSessionLocal
from db.models.metric_model import MetricModel
from services.worker.tasks import run_simulation_task
from services.redis.pubsub import AsyncRedisPubSub

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


async def consume_simulation_requests():
    consumer = AIOKafkaConsumer(
        settings.KAFKA_SIMULATION_TOPIC,
        bootstrap_servers=settings.KAFKA_BROKER,
        group_id="simulation-consumers",
        enable_auto_commit=True,
        auto_offset_reset="earliest",
    )

    await consumer.start()
    print(f"[Kafka] Listening on topic: {settings.KAFKA_SIMULATION_TOPIC}")

    try:
        async for msg in consumer:
            try:
                data = json.loads(msg.value.decode("utf-8"))
                command = data.get("command")
                user_id = data.get("user_id")
                if not command:
                    print(f"[Kafka] Invalid message: {data}")
                    continue
                print(f"[Kafka] Received simulation request: {command} (user_id={user_id})")
                run_simulation_task.delay(command, user_id)
            except Exception as e:
                print(f"[Kafka] Error processing message: {e}")
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
        "simulation_requests",
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
