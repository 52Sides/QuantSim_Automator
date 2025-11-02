import asyncio
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from services.redis.pubsub import AsyncRedisPubSub
import os

router = APIRouter(prefix="/ws", tags=["WebSocket Simulations"])

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
REDIS_CHANNEL = os.getenv("REDIS_PUBSUB_CHANNEL", "sim_progress")


@router.websocket("/simulations")
async def websocket_simulations(ws: WebSocket):
    await ws.accept()
    pubsub = AsyncRedisPubSub(REDIS_URL, REDIS_CHANNEL)
    await pubsub.connect()

    try:
        async for message in pubsub.subscribe():
            await ws.send_text(json.dumps(message))
    except WebSocketDisconnect:
        print("WebSocket disconnected")
    finally:
        await pubsub.close()
