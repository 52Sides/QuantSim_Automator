from pydantic import BaseModel, Field
from datetime import date


class SimulationRequest(BaseModel):
    ticker: str = Field(..., example="AAPL")
    start: date = Field(..., example="2020-01-01")
    end: date = Field(..., example="2021-01-01")


class SimulationResponse(BaseModel):
    ticker: str
    start: date
    end: date
    cagr: float
    sharpe: float
    max_drawdown: float
