import pytest
from core.command_parser import parse_command_safe, CommandValidationError


@pytest.mark.unit
def test_valid_command_single():
    cmd = "AAPL-L-100% 2020-01-01 2021-01-01"
    weights, sides, start, end = parse_command_safe(cmd)
    assert weights == {"AAPL": 1.0}
    assert sides == {"AAPL": "L"}
    assert start == "2020-01-01"
    assert end == "2021-01-01"


@pytest.mark.unit
def test_valid_command_multi():
    cmd = "TSLA-L-50% AAPL-S-50% 2020-01-01 2021-01-01"
    weights, sides, _, _ = parse_command_safe(cmd)
    assert weights["TSLA"] == 0.5
    assert sides["AAPL"] == "S"
    assert abs(sum(weights.values()) - 1.0) < 1e-6


@pytest.mark.unit
@pytest.mark.parametrize("bad_cmd", [
    "",  # пустая
    "AAPL-L-50% 2020-01-01",  # нет end
    "AAPL-L-200% 2020-01-01 2021-01-01",  # превышен вес
    "AAPL-X-50% 2020-01-01 2021-01-01",  # неверная сторона
    "AAPL-L-50% 2021-01-01 2020-01-01",  # start >= end
    "AAPL-L-50% 2010-01-01 2025-02-01",  # >10 лет
    "AAPL-L-50% " * 11 + "2020-01-01 2021-01-01",  # >10 тикеров
])
def test_invalid_commands(bad_cmd):
    with pytest.raises(CommandValidationError):
        parse_command_safe(bad_cmd)
