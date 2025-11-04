import asyncio, json
from aiokafka import AIOKafkaProducer

async def send():
    producer = AIOKafkaProducer(bootstrap_servers="kafka:9092")
    await producer.start()
    await producer.send_and_wait(
        "portfolio-events",
        json.dumps({
            "type": "simulation.completed",
            "job_id": "job777",
            "result_id": 1,
        }).encode("utf-8"),
    )
    await producer.stop()

asyncio.run(send())
