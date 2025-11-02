import asyncio
import json
from aiokafka import AIOKafkaConsumer
from services.worker.tasks import run_simulation_task
from core.config import settings


async def consume_simulation_requests():
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
                run_simulation_task.delay(cmd)
    finally:
        await consumer.stop()

if __name__ == "__main__":
    asyncio.run(consume_simulation_requests())
