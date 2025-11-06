from fastapi import APIRouter, Depends, HTTPException
from celery.result import AsyncResult
from services.worker.celery_app import celery_app
from schemas.simulation import SimulationRequest
from api.dependencies.users import get_current_user
from db.models.user_model import UserModel
from services.kafka.producer import producer

router = APIRouter(prefix="/simulate", tags=["Simulation Async"])


@router.post("/async/")
async def simulate_async(request: SimulationRequest, user: UserModel = Depends(get_current_user)):
    """Отправляет задачу симуляции в Kafka, где её подхватит consumer."""
    await producer.publish_simulation_request(request.command, user.id)
    return {"status": "queued", "user_id": user.id, "command": request.command}


@router.get("/status/{task_id}")
async def get_task_status(task_id: str):
    result = AsyncResult(task_id, app=celery_app)
    if not result:
        raise HTTPException(status_code=404, detail="Task not found")

    response = {"task_id": task_id, "status": result.status}
    if result.ready():
        response["result"] = result.result
    return response