from pydantic import BaseModel
from datetime import date
from typing import List, Dict

class PricePoint(BaseModel):
    date: str
    close: float


class SimulationRequest(BaseModel):
    ticker: str
    start: date
    end: date


class SimulationResponse(BaseModel):
    ticker: str
    start: date
    end: date
    cagr: float
    sharpe: float
    max_drawdown: float
    prices: List[PricePoint]
