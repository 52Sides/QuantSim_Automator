import json
from aiokafka import AIOKafkaProducer
from core.config import settings


class KafkaProducerService:
    def __init__(self, bootstrap_servers: str):
        self.bootstrap_servers = bootstrap_servers
        self._producer = None


    async def start(self):
        if not self._producer:
            self._producer = AIOKafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            )
            await self._producer.start()


    async def stop(self):
        if self._producer:
            await self._producer.stop()
            self._producer = None


    async def send(self, topic: str, message: dict):
        if not self._producer:
            await self.start()
        await self._producer.send_and_wait(topic, message)


    async def publish_simulation_request(self, command: str, user_id: int | None = None):
        """Публикует задачу симуляции в Kafka."""
        message = {"command": command, "user_id": user_id}
        await self.send(settings.KAFKA_SIMULATION_TOPIC, message)
        print(f"[Kafka] Published simulation request: {message}")


producer = KafkaProducerService(settings.KAFKA_BROKER)
