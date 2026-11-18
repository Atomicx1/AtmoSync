
from pathlib import Path

import pandas as pd


def calculate_spread_alerts(
    df: pd.DataFrame,
    spread_column: str = "spread",
    window: int = 5,
    multiplier: float = 2.0,
) -> pd.DataFrame:
    """
    Calculate rolling spread thresholds and flag unusual spreads.

    A high spread is flagged when it exceeds:
    rolling mean + (multiplier * rolling standard deviation).
    """

    if spread_column not in df.columns:
        raise ValueError(f"Missing column: {spread_column}")

    if window < 2:
        raise ValueError("Window must be at least 2.")

    if multiplier <= 0:
        raise ValueError("Multiplier must be positive.")

    result = df.copy()
    result[spread_column] = pd.to_numeric(
        result[spread_column], errors="raise"
    )

    if result[spread_column].isna().any():
        raise ValueError("Spread values cannot contain missing values.")

    if not result[spread_column].map(
        lambda value: pd.notna(value) and abs(value) != float("inf")
    ).all():
        raise ValueError("Spread values must be finite.")

    result["rolling_mean"] = (
        result[spread_column].rolling(window=window).mean()
    )

    result["rolling_std"] = (
        result[spread_column].rolling(window=window).std()
    )

    result["dynamic_threshold"] = (
        result["rolling_mean"] + multiplier * result["rolling_std"]
    )

    result["alert"] = (
        result[spread_column] > result["dynamic_threshold"]
    ).fillna(False)

    result["alert_status"] = result["alert"].map(
        {True: "HIGH SPREAD ALERT", False: "NORMAL"}
    )

    return result


if __name__ == "__main__":
    sample_data = pd.DataFrame({
        "spread": [10, 12, 11, 13, 12, 14, 15, 40, 16, 17]
    })

    output = calculate_spread_alerts(sample_data)

    print(output.to_string(index=False))

    output_dir = Path("reports")
    output_dir.mkdir(exist_ok=True)

    output.to_csv(
        output_dir / "spread_alerts.csv",
        index=False
    )

    print("\nAlert report saved to reports/spread_alerts.csv")
