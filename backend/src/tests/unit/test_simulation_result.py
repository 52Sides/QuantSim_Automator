import pandas as pd
from core.simulation_result import SimulationResult


def test_simulation_result_dataclass():
    rets = pd.Series([0.01, -0.02])
    cum = pd.Series([1.01, 0.99])
    result = SimulationResult(
        returns=rets,
        cumulative=cum,
        cagr=0.1,
        sharpe=1.2,
        max_drawdown=0.3,
        meta={"note": "test"},
    )
    assert result.cagr == 0.1
    assert result.meta["note"] == "test"
