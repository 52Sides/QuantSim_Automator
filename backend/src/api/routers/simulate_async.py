from fastapi import APIRouter, HTTPException
from celery.result import AsyncResult
from services.worker.celery_app import celery_app
from services.worker.tasks import run_simulation_task
from schemas.simulation import SimulationRequest

router = APIRouter(prefix="/simulate", tags=["Simulation Async"])

@router.post("/async")
async def start_simulation(request: SimulationRequest):
    """Создаёт асинхронную задачу симуляции."""
    task = run_simulation_task.delay(request.command)
    return {"task_id": task.id, "status": "PENDING"}


@router.get("/status/{task_id}")
async def get_task_status(task_id: str):
    """Проверка статуса задачи симуляции."""
    result = AsyncResult(task_id, app=celery_app)
    if not result:
        raise HTTPException(status_code=404, detail="Task not found")

    response = {"task_id": task_id, "status": result.status}
    if result.ready():
        response["result"] = result.result
    return response
