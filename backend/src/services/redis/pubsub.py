import json
import redis.asyncio as redis


class AsyncRedisPubSub:
    """Асинхронная обёртка для Redis Pub/Sub — используется для уведомлений симуляции."""

    def __init__(self, url: str, channel: str):
        self.url = url
        self.channel = channel
        self._redis = None
        self._pubsub = None

    async def connect(self):
        """Создаёт подключение к Redis (один клиент на весь экземпляр)."""
        if self._redis is None:
            self._redis = redis.from_url(self.url, decode_responses=True)

    async def publish(self, message: dict):
        """Публикует сообщение в канал."""
        if not self._redis:
            await self.connect()
        await self._redis.publish(self.channel, json.dumps(message))

    async def subscribe(self):
        """
        Асинхронный генератор событий.
        Пример использования:
            async for event in pubsub.subscribe():
                ...
        """
        if not self._redis:
            await self.connect()
        self._pubsub = self._redis.pubsub()
        await self._pubsub.subscribe(self.channel)

        async for msg in self._pubsub.listen():
            if msg["type"] == "message":
                try:
                    yield json.loads(msg["data"])
                except json.JSONDecodeError:
                    yield {"raw": msg["data"]}

    async def close(self):
        if self._pubsub:
            await self._pubsub.unsubscribe(self.channel)
            await self._pubsub.close()
            self._pubsub = None
        if self._redis:
            await self._redis.close()
            self._redis = None
