import redis.asyncio as aioredis
import json
import os

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")
redis_client = aioredis.from_url(REDIS_URL, decode_responses=True)

async def set_report_status(sim_id: int, status: str, path: str | None = None):
    data = {"status": status}
    if path:
        data["path"] = path
    await redis_client.hset(f"report:{sim_id}", mapping=data)

async def get_report_status(sim_id: int):
    res = await redis_client.hgetall(f"report:{sim_id}")
    return res or None
