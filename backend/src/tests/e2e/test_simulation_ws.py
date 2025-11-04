import asyncio
import json
import pytest
import websockets
from services.redis.pubsub import AsyncRedisPubSub

@pytest.mark.asyncio
async def test_simulation_completed_ws_flow(monkeypatch):
    """
    E2E тест WebSocket: проверяем, что после симуляции клиент получает событие
    simulation.completed через WebSocket.
    """

    # Мокаем Redis Pub/Sub
    class MockPubSub:
        async def listen(self):
            await asyncio.sleep(0.1)  # имитация задержки
            yield {
                "type": "message",
                "data": json.dumps({
                    "type": "simulation.completed",
                    "job_id": "job123",
                    "result_id": 42
                })
            }

    async def fake_subscribe(self):
        return MockPubSub()

    # Патчим метод subscribe у нашего Redis PubSub
    monkeypatch.setattr(AsyncRedisPubSub, "subscribe", fake_subscribe)

    # Подключаемся к WebSocket
    uri = "ws://localhost:8000/ws/simulations"  # сервер должен быть поднят
    async with websockets.connect(uri) as ws:
        # Получаем сообщение от сервера
        msg = await ws.recv()
        data = json.loads(msg)

        # Проверяем данные
        assert data["type"] == "simulation.completed"
        assert data["job_id"] == "job123"
        assert data["result_id"] == 42
