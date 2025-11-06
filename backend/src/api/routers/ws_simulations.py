from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json
from core.config import settings
from services.redis.pubsub import AsyncRedisPubSub

router = APIRouter()

@router.websocket("/ws/simulations")
async def websocket_simulations(ws: WebSocket):
    """WebSocket для стриминга прогресса симуляций."""
    await ws.accept()
    pubsub = AsyncRedisPubSub(settings.REDIS_URL, "simulations")
    await pubsub.connect()

    try:
        async for event in pubsub.subscribe():
            await ws.send_text(json.dumps(event))
    except WebSocketDisconnect:
        print("[WS] Client disconnected")
    except Exception as e:
        await ws.send_text(json.dumps({"error": str(e)}))
    finally:
        await pubsub.close()
        await ws.close()
