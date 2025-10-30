import re
from datetime import datetime
from typing import Dict, Tuple

MAX_TICKERS = 10
MAX_CMD_LENGTH = 500
TICKER_RE = re.compile(r'^[A-Z0-9\.\-]{1,6}$')


class CommandValidationError(ValueError):
    """Ошибка валидации команды."""
    pass


def parse_command_safe(cmd: str) -> Tuple[Dict[str, float], Dict[str, str], str, str]:
    """
    Безопасно парсит команду формата:
    'TSLA-L-20% AAPL-S-80% 2020-01-01 2021-01-01'
    """
    if not isinstance(cmd, str):
        raise CommandValidationError("Command must be a string")

    cmd = cmd.strip()
    if not cmd or len(cmd) > MAX_CMD_LENGTH:
        raise CommandValidationError("Command too long or empty")

    parts = cmd.split()
    if len(parts) < 3:
        raise CommandValidationError("Invalid format: expected tickers and start/end dates")

    # Даты
    start, end = parts[-2], parts[-1]
    try:
        start_dt = datetime.fromisoformat(start)
        end_dt = datetime.fromisoformat(end)
        if start_dt >= end_dt:
            raise CommandValidationError("Start date must be before end date")
        if (end_dt.year - start_dt.year) > 10:
            raise CommandValidationError("Date range too long (>10 years)")
    except Exception:
        raise CommandValidationError("Invalid date format (expected YYYY-MM-DD)")

    tickers_raw = parts[:-2]
    if len(tickers_raw) > MAX_TICKERS:
        raise CommandValidationError("Too many tickers (max 10)")

    weights: Dict[str, float] = {}
    sides: Dict[str, str] = {}
    total_weight = 0.0

    for token in tickers_raw:
        m = re.match(r'^([A-Z0-9\.\-]{1,6})-([LS])-([0-9]{1,3})%$', token)
        if not m:
            raise CommandValidationError(f"Invalid token: {token}. Expected 'TICKER-L-50%' format.")
        ticker, side, weight_str = m.groups()
        if not TICKER_RE.match(ticker):
            raise CommandValidationError(f"Invalid ticker: {ticker}")
        weight = float(weight_str)
        if not (0 < weight <= 100):
            raise CommandValidationError(f"Invalid weight: {weight_str}")
        weights[ticker] = weight / 100.0
        sides[ticker] = side
        total_weight += weight

    if not (99.9 <= total_weight <= 100.1):
        raise CommandValidationError(f"Weights must sum to 100%, got {total_weight:.2f}%")

    return weights, sides, start, end
