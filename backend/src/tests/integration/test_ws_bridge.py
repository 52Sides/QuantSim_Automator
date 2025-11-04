import json
import pytest
from httpx import AsyncClient
from starlette.websockets import WebSocketDisconnect

@pytest.mark.asyncio
async def test_ws_receives_kafka_event(monkeypatch, async_client: AsyncClient):
    # mock Redis Pub/Sub
    from services.redis.pubsub import AsyncRedisPubSub

    class MockPubSub:
        async def listen(self):
            yield {"type": "message", "data": json.dumps({"type": "simulation.completed", "job_id": "123"})}

    async def fake_subscribe(self): return MockPubSub()
    monkeypatch.setattr(AsyncRedisPubSub, "subscribe", fake_subscribe)

    async with async_client.websocket_connect("/ws/simulations") as ws:
        msg = await ws.receive_json()
        assert msg["type"] == "simulation.completed"
        assert msg["job_id"] == "123"
