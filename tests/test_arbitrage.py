
import pytest

from src.analytics.arbitrage import (
    Trade,
    calculate_arbitrage
)


def test_profitable_trade():

    trade = Trade(
        "Avocado", 100, 140, 100,
        500, 200, 300, 5
    )

    result = calculate_arbitrage(trade)

    assert result["net_profit"] == pytest.approx(2300)
    assert result["profitable"] is True


def test_unprofitable_trade():

    trade = Trade(
        "Avocado", 150, 100, 100,
        500, 200, 300, 5
    )

    result = calculate_arbitrage(trade)

    assert result["net_profit"] < 0
    assert result["profitable"] is False


def test_invalid_spoilage():

    trade = Trade(
        "Avocado", 100, 140, 100,
        500, 200, 300, 120
    )

    with pytest.raises(ValueError):
        calculate_arbitrage(trade)


def test_zero_quantity():

    trade = Trade(
        "Avocado", 100, 140, 0,
        500, 200, 300, 5
    )

    with pytest.raises(ValueError):
        calculate_arbitrage(trade)
