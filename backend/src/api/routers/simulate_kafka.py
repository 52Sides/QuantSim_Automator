from fastapi import APIRouter, HTTPException
from services.kafka.producer import producer
from schemas.simulation import SimulationRequest
from core.config import settings

router = APIRouter(prefix="/simulate", tags=["Simulation Kafka"])

@router.post("/kafka")
async def enqueue_simulation(request: SimulationRequest):
    """Отправляет команду симуляции в Kafka."""
    try:
        await producer.send(settings.KAFKA_SIMULATION_TOPIC, {"command": request.command})
        return {"status": "queued", "broker": settings.KAFKA_BROKER}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
