from fastapi import FastAPI
from backend.routers import simulate

app = FastAPI(
    title="QuantSim Automator API",
    description="API для симуляции портфеля и расчёта метрик",
    version="0.2.0",
)

app.include_router(simulate.router)
