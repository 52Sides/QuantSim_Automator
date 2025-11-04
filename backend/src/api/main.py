from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routers import (
    simulate, system, simulations_history, simulate_async, simulate_tasks, simulate_kafka,
    ws_simulations, auth, auth_refresh
)

app = FastAPI(
    title="QuantSim Automator API",
    description="API для симуляции портфеля и расчёта метрик",
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173", "http://frontend:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(simulate.router)
app.include_router(simulate_async.router)
app.include_router(simulate_tasks.router)
app.include_router(system.router)
app.include_router(simulations_history.router)
app.include_router(simulate_kafka.router)
app.include_router(ws_simulations.router)
app.include_router(auth.router)
app.include_router(auth_refresh.router)

