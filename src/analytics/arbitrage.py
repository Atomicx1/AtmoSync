
from dataclasses import dataclass


@dataclass
class Trade:
    commodity: str
    buy_price: float
    sell_price: float
    quantity_kg: float
    transport_cost: float
    handling_cost: float
    storage_cost: float
    spoilage_percentage: float


def calculate_arbitrage(trade):

    values = [
        trade.buy_price,
        trade.sell_price,
        trade.quantity_kg,
        trade.transport_cost,
        trade.handling_cost,
        trade.storage_cost,
        trade.spoilage_percentage
    ]

    if not all(isinstance(v, (int, float)) for v in values):
        raise ValueError("All inputs must be numeric.")

    if not all(__import__("math").isfinite(v) for v in values):
        raise ValueError("Inputs must be finite numbers.")

    if any(v < 0 for v in values):
        raise ValueError("Inputs cannot be negative.")

    if trade.quantity_kg <= 0:
        raise ValueError("Quantity must be positive.")

    if not 0 <= trade.spoilage_percentage <= 100:
        raise ValueError("Invalid spoilage percentage.")

    purchase_cost = (
        trade.buy_price * trade.quantity_kg
    )

    expected_wastage = (
        trade.spoilage_percentage / 100
    )

    sellable_quantity = (
        trade.quantity_kg * (1 - expected_wastage)
    )

    revenue = (
        trade.sell_price * sellable_quantity
    )

    operating_cost = (
        purchase_cost
        + trade.transport_cost
        + trade.handling_cost
        + trade.storage_cost
    )

    net_profit = revenue - operating_cost

    roi = (
        net_profit / operating_cost * 100
        if operating_cost > 0 else 0
    )

    return {
        "commodity": trade.commodity,
        "purchase_cost": purchase_cost,
        "sellable_quantity_kg": sellable_quantity,
        "expected_revenue": revenue,
        "total_cost": operating_cost,
        "net_profit": net_profit,
        "roi_percentage": roi,
        "profitable": net_profit > 0
    }


if __name__ == "__main__":

    sample = Trade(
        commodity="Avocado",
        buy_price=100,
        sell_price=140,
        quantity_kg=100,
        transport_cost=500,
        handling_cost=200,
        storage_cost=300,
        spoilage_percentage=5
    )

    result = calculate_arbitrage(sample)

    for key, value in result.items():
        print(f"{key}: {value}")
