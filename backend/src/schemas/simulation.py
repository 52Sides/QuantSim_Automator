from pydantic import BaseModel
from datetime import date
from typing import List


class PortfolioPoint(BaseModel):
    date: str
    portfolio_value: float


class SimulationRequest(BaseModel):
    command: str  # пример: "TSLA-S-20% AAPL-L-80% 2020-05-01 2021-05-01"


class SimulationResponse(BaseModel):
    cagr: float
    sharpe: float
    max_drawdown: float
    portfolio: List[PortfolioPoint]
