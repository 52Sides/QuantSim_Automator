import asyncio
import json
import aioredis


class AsyncRedisPubSub:
    """Обёртка для Redis Pub/Sub, используется для стриминга прогресса симуляции."""

    def __init__(self, url: str, channel: str):
        self.url = url
        self.channel = channel
        self._redis = None

    async def connect(self):
        if self._redis is None:
            self._redis = await aioredis.from_url(self.url, decode_responses=True)

    async def publish(self, message: dict):
        """Публикация сообщения в канал."""
        if not self._redis:
            await self.connect()
        await self._redis.publish(self.channel, json.dumps(message))

    async def subscribe(self):
        """Создаёт подписку на канал и возвращает асинхронный генератор сообщений."""
        if not self._redis:
            await self.connect()
        pubsub = self._redis.pubsub()
        await pubsub.subscribe(self.channel)

        async for msg in pubsub.listen():
            if msg["type"] == "message":
                yield json.loads(msg["data"])

    async def close(self):
        if self._redis:
            await self._redis.close()
            self._redis = None
