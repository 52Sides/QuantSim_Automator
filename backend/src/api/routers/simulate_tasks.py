from fastapi import APIRouter
from services.worker.celery_app import celery_app

router = APIRouter(prefix="/simulate", tags=["Simulation Tasks"])

@router.get("/tasks")
async def list_active_tasks():
    """Возвращает список активных задач Celery."""
    insp = celery_app.control.inspect()
    active = insp.active() or {}
    result = []
    for worker, tasks in active.items():
        for t in tasks:
            result.append({
                "worker": worker,
                "id": t.get("id"),
                "name": t.get("name"),
                "args": t.get("args"),
                "state": "ACTIVE"
            })
    return result
