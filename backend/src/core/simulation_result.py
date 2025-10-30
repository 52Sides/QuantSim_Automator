from dataclasses import dataclass
import pandas as pd
from typing import Dict, Any

@dataclass
class SimulationResult:
    """Результат симуляции."""
    returns: pd.Series
    cumulative: pd.Series
    cagr: float
    sharpe: float
    max_drawdown: float
    meta: Dict[str, Any]
