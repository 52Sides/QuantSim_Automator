from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from services.reports_cache import get_report_status
from services.worker.tasks import generate_report_task
from pathlib import Path

router = APIRouter(prefix="/report", tags=["Reports"])

@router.get("/{simulation_id}")
async def get_report(simulation_id: int):
    """Если отчёт уже готов — возвращаем файл, иначе запускаем задачу."""
    status = await get_report_status(simulation_id)
    if status and status.get("status") == "ready":
        path = Path(status["path"])
        if not path.exists():
            raise HTTPException(404, "Report file missing")
        return FileResponse(path, filename=f"report_{simulation_id}.xlsx")

    # если отчёта нет — создаём задачу Celery
    generate_report_task.delay(simulation_id)
    return {"status": "queued"}
