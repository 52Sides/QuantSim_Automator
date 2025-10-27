from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routers import simulate

app = FastAPI(
    title="QuantSim Automator API",
    description="API для симуляции портфеля и расчёта метрик",
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(simulate.router)
